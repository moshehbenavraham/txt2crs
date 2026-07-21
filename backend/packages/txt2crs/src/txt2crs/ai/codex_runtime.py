# SPDX-License-Identifier: MIT-0

"""Subscription-only policy around an official Codex SDK adapter.

SDK-specific types stop at the ``CodexAdapter`` boundary. This keeps the course
pipeline deterministic under tests and makes beta SDK upgrades a focused
contract change.
"""

import json
import os
from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from hashlib import sha256
from ipaddress import ip_address
from pathlib import Path
from time import monotonic
from typing import Any, TypeVar, cast
from urllib.parse import urlsplit

from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox
from openai_codex.types import Personality
from pydantic import BaseModel, ValidationError

from txt2crs.ai.errors import (
    RuntimeErrorCode,
    RuntimeTimeoutError,
    classify_runtime_error,
)
from txt2crs.ai.events import RuntimeEvent, RuntimeEventType, stable_tool_call_id
from txt2crs.ai.model_policy import Gpt56ModelPolicy, ModelPolicyError
from txt2crs.ai.runtime import (
    CancellationToken,
    CodexAdapter,
    CodexAdapterResult,
    TurnRequest,
)
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import RuntimeUsage, SubscriptionQuotaState

ArtifactType = TypeVar("ArtifactType", bound=BaseModel)
_UNSUPPORTED_PROVIDER_SCHEMA_KEYWORDS = frozenset(
    {
        # The current Codex structured-output boundary does not accept dynamic
        # object keys. Pydantic emits these keywords for validated mappings,
        # such as ReviewPack.section_summaries.
        "patternProperties",
        "propertyNames",
    }
)


class RuntimePolicyError(RuntimeError):
    """A permanent subscription, model, or schema-policy rejection."""


class InvalidModelOutputError(RuntimePolicyError):
    """A completed turn whose output failed the strict local schema."""

    def __init__(self, message: str, *, usage: RuntimeUsage) -> None:
        self.usage = usage
        super().__init__(message)


def _contains_unsupported_provider_schema_keyword(schema_value: object) -> bool:
    """Return whether a Pydantic schema exceeds the provider's strict subset."""

    if isinstance(schema_value, dict):
        if _UNSUPPORTED_PROVIDER_SCHEMA_KEYWORDS.intersection(schema_value):
            return True
        return any(
            _contains_unsupported_provider_schema_keyword(child_value)
            for child_value in schema_value.values()
        )
    if isinstance(schema_value, list):
        return any(
            _contains_unsupported_provider_schema_keyword(child_value)
            for child_value in schema_value
        )
    return False


def _strict_provider_output_schema(
    pydantic_schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert one supported Pydantic schema to Codex's strict object contract.

    Pydantic represents a field with a default as optional even when its value
    type already includes ``null``. The current bundled runtime requires every
    declared property in ``required`` and rejects JSON Schema defaults. This
    detached recursive copy preserves local constraints while making nullable
    fields explicit instead of silently dropping them.
    """

    strict_schema = cast(
        dict[str, Any],
        json.loads(json.dumps(pydantic_schema)),
    )

    def normalize_schema_node(schema_node: object) -> None:
        if isinstance(schema_node, dict):
            schema_node.pop("default", None)
            properties = schema_node.get("properties")
            if isinstance(properties, dict):
                schema_node["required"] = list(properties)
                schema_node["additionalProperties"] = False
            for child_value in schema_node.values():
                normalize_schema_node(child_value)
            return
        if isinstance(schema_node, list):
            for child_value in schema_node:
                normalize_schema_node(child_value)

    normalize_schema_node(strict_schema)
    return strict_schema


def _prepare_provider_turn(
    *,
    request: TurnRequest,
    artifact_model: type[BaseModel],
) -> tuple[TurnRequest, dict[str, Any] | None]:
    """
    Select strict provider enforcement or a trusted-schema local fallback.

    The fallback is deliberately narrow: it is used only when the canonical
    Pydantic schema contains dynamic mapping keywords that the provider schema
    cannot express. The exact schema remains trusted prompt material, and the
    returned object must still pass the same Pydantic model before acceptance.
    """

    pydantic_schema = artifact_model.model_json_schema()
    if not _contains_unsupported_provider_schema_keyword(pydantic_schema):
        return request, _strict_provider_output_schema(pydantic_schema)

    trusted_schema_json = json.dumps(
        pydantic_schema,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    schema_prompt_request = TurnRequest(
        **request.model_dump(exclude={"trusted_instructions"}),
        trusted_instructions=(
            f"{request.trusted_instructions}\n\n"
            "Return exactly one JSON object matching this trusted JSON Schema. "
            "Do not wrap it in Markdown:\n"
            f"{trusted_schema_json}"
        ),
    )
    return schema_prompt_request, None


@dataclass(frozen=True, slots=True)
class ResearchMcpConnection:
    """A required loopback MCP endpoint owned by the application worker."""

    url: str
    startup_timeout_seconds: int = 10
    tool_timeout_seconds: int = 60

    def __post_init__(self) -> None:
        """Reject remote endpoints and ambiguous URL credentials."""

        parsed_url = urlsplit(self.url)
        hostname = parsed_url.hostname
        is_loopback = hostname == "localhost"
        if hostname is not None and not is_loopback:
            try:
                is_loopback = ip_address(hostname).is_loopback
            except ValueError:
                is_loopback = False
        if (
            parsed_url.scheme != "http"
            or not is_loopback
            or parsed_url.port is None
            or parsed_url.path != "/mcp"
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise ValueError(
                "Research MCP URL must be an explicit loopback HTTP /mcp endpoint."
            )
        if self.startup_timeout_seconds <= 0 or self.tool_timeout_seconds <= 0:
            raise ValueError("Research MCP timeouts must be positive.")

    def codex_config_overrides(self) -> tuple[str, ...]:
        """Return exact CLI overrides with only the two reviewed research tools."""

        prefix = "mcp_servers.txt2crs_research"
        return (
            f"{prefix}.url={json.dumps(self.url)}",
            (f'{prefix}.enabled_tools=["research_search","research_extract"]'),
            f"{prefix}.required=true",
            f"{prefix}.startup_timeout_sec={self.startup_timeout_seconds}",
            f"{prefix}.tool_timeout_sec={self.tool_timeout_seconds}",
            f'{prefix}.default_tools_approval_mode="approve"',
        )


@dataclass(frozen=True, slots=True)
class ValidatedTurnResult[ArtifactType: BaseModel]:
    """Locally validated artifact plus private turn accounting."""

    artifact: ArtifactType
    usage: RuntimeUsage
    thread_id: str
    turn_id: str


@dataclass(frozen=True, slots=True)
class _StreamedTurnResult:
    """SDK-shaped values retained after safe notification projection."""

    id: str
    status: object
    final_response: str | None
    usage: object | None


class CodexSubscriptionRuntime:
    """Validate account, model, schema, cancellation, and usage for each turn."""

    _REMOVED_CHILD_ENVIRONMENT_KEYS = frozenset(
        {
            "OPENAI_API_KEY",
            "CODEX_API_KEY",
            "TAVILY_API_KEY",
        }
    )

    def __init__(
        self,
        *,
        adapter: CodexAdapter,
        model_policy: Gpt56ModelPolicy,
    ) -> None:
        self._adapter = adapter
        self._model_policy = model_policy

    @classmethod
    def build_child_environment(
        cls,
        parent_environment: Mapping[str, str],
        *,
        codex_home: Path,
    ) -> dict[str, str]:
        """Remove secrets and bind the worker to one explicit credential root."""

        if not codex_home.is_absolute():
            raise ValueError("CODEX_HOME must be an absolute path.")
        child_environment = {
            key: value
            for key, value in parent_environment.items()
            if key.upper() not in {*cls._REMOVED_CHILD_ENVIRONMENT_KEYS, "CODEX_HOME"}
        }
        child_environment["CODEX_HOME"] = str(codex_home)
        return child_environment

    def inspect_readiness(self) -> RuntimeReadiness:
        """Return a browser-safe account/model/quota readiness projection."""

        try:
            account_type = self._adapter.inspect_account_type()
            if account_type != "chatgpt":
                return RuntimeReadiness.create(
                    status=RuntimeReadinessStatus.unavailable,
                    credential_status=(
                        CredentialStatus.valid
                        if account_type == "api_key"
                        else CredentialStatus.unknown
                    ),
                    model_entitled=False,
                    subscription_quota_state=SubscriptionQuotaState.unknown,
                    warnings=["Subscription-only mode requires a ChatGPT account."],
                    recovery_actions=["Sign in with an eligible ChatGPT account."],
                )
            available_model_ids = self._adapter.list_model_ids()
        except Exception as readiness_error:
            classified_error = classify_runtime_error(readiness_error)
            credential_status = (
                CredentialStatus.reauthentication_required
                if classified_error.code is RuntimeErrorCode.reauthentication_required
                else CredentialStatus.unknown
            )
            return RuntimeReadiness.create(
                status=RuntimeReadinessStatus.unavailable,
                credential_status=credential_status,
                model_entitled=False,
                subscription_quota_state=SubscriptionQuotaState.unknown,
                warnings=[classified_error.public_message],
                recovery_actions=(
                    ["Sign in to ChatGPT again."]
                    if credential_status is CredentialStatus.reauthentication_required
                    else ["Retry the runtime readiness check."]
                ),
            )

        try:
            self._model_policy.require_discovered(available_model_ids)
        except ModelPolicyError:
            model_entitled = False
        else:
            model_entitled = True
        return RuntimeReadiness.create(
            status=(
                RuntimeReadinessStatus.ready
                if model_entitled
                else RuntimeReadinessStatus.unavailable
            ),
            credential_status=CredentialStatus.valid,
            model_entitled=model_entitled,
            # The pinned public Python SDK exposes account state and per-turn
            # token usage, but not app-server's rate-limit read operation.
            subscription_quota_state=SubscriptionQuotaState.unknown,
            warnings=(
                [
                    "Subscription quota is not exposed by the pinned public "
                    "Codex Python SDK."
                ]
                if model_entitled
                else ["The configured GPT-5.6 model is not available for this account."]
            ),
            recovery_actions=(
                []
                if model_entitled
                else ["Review the configured GPT-5.6 model and account access."]
            ),
        )

    def run_validated_turn(
        self,
        *,
        request: TurnRequest,
        artifact_model: type[ArtifactType],
        cancellation: CancellationToken,
    ) -> ValidatedTurnResult[ArtifactType]:
        """Run one turn and accept output only after exact local validation."""

        cancellation.raise_if_cancelled()
        if self._adapter.inspect_account_type() != "chatgpt":
            raise RuntimePolicyError(
                "Subscription-only mode requires an authenticated ChatGPT account."
            )

        available_model_ids = self._adapter.list_model_ids()
        try:
            self._model_policy.require_turn_model(
                requested_model_id=request.model_id,
                discovered_model_ids=available_model_ids,
            )
        except ModelPolicyError as model_policy_error:
            raise RuntimePolicyError(str(model_policy_error)) from None

        started_at = monotonic()
        provider_request, provider_output_schema = _prepare_provider_turn(
            request=request,
            artifact_model=artifact_model,
        )
        adapter_result = self._adapter.run_turn(
            request=provider_request,
            output_schema=provider_output_schema,
            cancellation=cancellation,
        )
        cancellation.raise_if_cancelled()
        try:
            self._model_policy.require_result_model(
                requested_model_id=request.model_id,
                result_model_id=adapter_result.model_id,
            )
        except ModelPolicyError as model_policy_error:
            raise RuntimePolicyError(str(model_policy_error)) from None
        usage = RuntimeUsage.for_chatgpt_subscription(
            model_id=adapter_result.model_id,
            input_tokens=adapter_result.input_tokens,
            output_tokens=adapter_result.output_tokens,
            latency_ms=max(0, round((monotonic() - started_at) * 1_000)),
        )
        try:
            artifact = artifact_model.model_validate(adapter_result.output)
        except ValidationError as validation_error:
            raise InvalidModelOutputError(
                "Codex returned output that failed local schema validation.",
                usage=usage,
            ) from validation_error

        return ValidatedTurnResult(
            artifact=artifact,
            usage=usage,
            thread_id=adapter_result.thread_id,
            turn_id=adapter_result.turn_id,
        )


class OfficialCodexSdkAdapter:
    """Concrete adapter for the pinned official ``openai-codex`` Python SDK."""

    def __init__(
        self,
        *,
        client: Any,
        polling_seconds: float = 0.05,
        event_sink: Callable[[RuntimeEvent], None] | None = None,
    ) -> None:
        if polling_seconds <= 0:
            raise ValueError("polling_seconds must be positive")
        self._client = client
        self._polling_seconds = polling_seconds
        self._event_sink = event_sink

    @staticmethod
    def build_config_overrides(
        *,
        research_mcp: ResearchMcpConnection | None,
    ) -> tuple[str, ...]:
        """Return the pinned safe layer applied over owner Codex settings."""

        baseline_overrides = (
            # Clear every user-configured MCP endpoint even when this job does
            # not enable research. Only the reviewed loopback endpoint may be
            # appended below.
            "mcp_servers={}",
            # Newer Codex releases may persist values that this pinned runtime
            # cannot parse. Use a supported value at the version boundary.
            'model_reasoning_effort="high"',
            # Headless workers do not have an OS secrets service. Selecting the
            # documented file store avoids a noisy keyring attempt before the
            # same file-backed fallback that the worker would use anyway.
            'mcp_oauth_credentials_store="file"',
        )
        return baseline_overrides + (
            research_mcp.codex_config_overrides() if research_mcp is not None else ()
        )

    @classmethod
    def create(
        cls,
        *,
        worker_directory: Path,
        codex_home: Path,
        parent_environment: Mapping[str, str] | None = None,
        polling_seconds: float = 0.05,
        research_mcp: ResearchMcpConnection | None = None,
        event_sink: Callable[[RuntimeEvent], None] | None = None,
    ) -> "OfficialCodexSdkAdapter":
        """Launch the pinned SDK in an isolated caller-provided worker root."""

        if worker_directory.is_symlink() or codex_home.is_symlink():
            raise ValueError("Worker and CODEX_HOME directories cannot be symlinks.")
        worker_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        worker_directory.chmod(0o700)
        codex_home.mkdir(mode=0o700, parents=True, exist_ok=True)
        codex_home.chmod(0o700)
        environment = CodexSubscriptionRuntime.build_child_environment(
            parent_environment or os.environ,
            codex_home=codex_home.resolve(strict=True),
        )
        config = CodexConfig(
            cwd=str(worker_directory),
            env=environment,
            config_overrides=cls.build_config_overrides(research_mcp=research_mcp),
            client_name="txt2crs",
            client_title="txt2crs Course Generator",
        )
        return cls(
            client=Codex(config),
            polling_seconds=polling_seconds,
            event_sink=event_sink,
        )

    def close(self) -> None:
        """Close the SDK and its pinned app-server process."""

        self._client.close()

    def inspect_account_type(self) -> str:
        """Normalize the SDK account union to local policy values."""

        # The public SDK delegates any refresh to Codex. txt2crs receives only
        # the normalized account union and never reads or stores token bytes.
        account_response = self._client.account(refresh_token=True)
        account = getattr(account_response, "account", None)
        account_root = getattr(account, "root", None)
        account_type = getattr(account_root, "type", None)
        if account_type == "chatgpt":
            return "chatgpt"
        if account_type == "apiKey":
            return "api_key"
        return "unknown"

    def list_model_ids(self) -> tuple[str, ...]:
        """Return stable, deduplicated model slugs reported by app-server."""

        model_response = self._client.models()
        model_ids = {
            str(model.model)
            for model in getattr(model_response, "data", [])
            if getattr(model, "model", None)
        }
        return tuple(sorted(model_ids))

    def run_turn(
        self,
        *,
        request: TurnRequest,
        output_schema: dict[str, Any] | None,
        cancellation: CancellationToken,
    ) -> CodexAdapterResult:
        """Run a schema turn and interrupt on cancellation or local deadline."""

        cancellation.raise_if_cancelled()
        thread = self._client.thread_start(
            model=request.model_id,
            approval_mode=ApprovalMode.deny_all,
            sandbox=Sandbox.read_only,
            ephemeral=True,
            # Keep the selected model's base metadata intact. Codex clears its
            # personality metadata whenever callers replace base instructions,
            # which made the explicit ``none`` value produce a false fallback
            # warning. Developer instructions are the intended trusted layer.
            personality=Personality.none,
            developer_instructions=request.trusted_instructions,
        )
        turn_handle = thread.turn(
            request.prompt,
            output_schema=output_schema,
            model=request.model_id,
        )
        executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="txt2crs-codex-turn",
        )
        future = executor.submit(
            self._consume_turn,
            turn_handle,
            str(thread.id),
            request.stage,
        )
        deadline = monotonic() + request.timeout_seconds
        try:
            while True:
                if cancellation.is_cancelled:
                    turn_handle.interrupt()
                    raise RuntimeError("The model turn was cancelled.")
                remaining_seconds = deadline - monotonic()
                if remaining_seconds <= 0:
                    turn_handle.interrupt()
                    raise RuntimeTimeoutError("The model turn exceeded its deadline.")
                try:
                    turn_result = future.result(
                        timeout=min(self._polling_seconds, remaining_seconds)
                    )
                    break
                except FutureTimeoutError:
                    continue
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        turn_status = getattr(turn_result.status, "value", turn_result.status)
        if turn_status != "completed":
            raise RuntimeError("The Codex turn did not complete successfully.")
        if not turn_result.final_response:
            raise RuntimeError("The Codex turn returned no final response.")
        try:
            parsed_output = json.loads(turn_result.final_response)
        except json.JSONDecodeError as json_error:
            raise ValueError("The Codex turn returned malformed JSON.") from json_error
        if not isinstance(parsed_output, dict):
            raise ValueError("The Codex turn output must be a JSON object.")

        usage = getattr(turn_result, "usage", None)
        last_usage = getattr(usage, "last", None)
        input_tokens = getattr(last_usage, "input_tokens", None)
        output_tokens = getattr(last_usage, "output_tokens", None)
        return CodexAdapterResult(
            output=parsed_output,
            thread_id=str(thread.id),
            turn_id=str(turn_result.id),
            model_id=request.model_id,
            input_tokens=(int(input_tokens) if isinstance(input_tokens, int) else None),
            output_tokens=(
                int(output_tokens) if isinstance(output_tokens, int) else None
            ),
        )

    def _consume_turn(
        self,
        turn_handle: Any,
        thread_id: str,
        stage: str,
    ) -> Any:
        """Use the SDK collector normally, or project its stream when requested."""

        if self._event_sink is None:
            return turn_handle.run()

        final_response: str | None = None
        token_usage: object | None = None
        completed_turn: object | None = None
        event_sequence = 0
        for notification in turn_handle.stream():
            method = str(getattr(notification, "method", ""))
            payload = getattr(notification, "payload", None)
            if method == "turn/started":
                event_sequence += 1
                self._emit_runtime_event(
                    event_sequence=event_sequence,
                    event_type=RuntimeEventType.turn_started,
                    stage=stage,
                    thread_id=thread_id,
                    turn_id=str(turn_handle.id),
                    safe_message="Model stage started.",
                )
                continue

            if method in {"item/started", "item/completed"}:
                item_wrapper = getattr(payload, "item", None)
                item = getattr(item_wrapper, "root", item_wrapper)
                item_type = str(getattr(item, "type", ""))
                if item_type == "mcpToolCall":
                    tool_name = str(getattr(item, "tool", "research tool"))
                    display_tool_name = (
                        tool_name
                        if tool_name in {"research_search", "research_extract"}
                        else "research"
                    )
                    provider_call_id = str(getattr(item, "id", "unknown-call"))
                    event_sequence += 1
                    self._emit_runtime_event(
                        event_sequence=event_sequence,
                        event_type=(
                            RuntimeEventType.tool_started
                            if method == "item/started"
                            else RuntimeEventType.tool_completed
                        ),
                        stage=stage,
                        thread_id=thread_id,
                        turn_id=str(turn_handle.id),
                        safe_message=(
                            f"Research tool {display_tool_name} "
                            f"{'started' if method == 'item/started' else 'completed'}."
                        ),
                        tool_call_id=stable_tool_call_id(
                            thread_id=thread_id,
                            turn_id=str(turn_handle.id),
                            provider_call_id=provider_call_id,
                            tool_name=tool_name,
                        ),
                    )
                elif method == "item/completed" and item_type == "agentMessage":
                    message_text = getattr(item, "text", None)
                    if isinstance(message_text, str):
                        # The final schema response is consumed privately. It
                        # is never copied into progress events.
                        final_response = message_text
                continue

            if method == "thread/tokenUsage/updated":
                token_usage = getattr(payload, "token_usage", None)
                last_usage = getattr(token_usage, "last", None)
                input_tokens = getattr(last_usage, "input_tokens", None)
                output_tokens = getattr(last_usage, "output_tokens", None)
                event_sequence += 1
                self._emit_runtime_event(
                    event_sequence=event_sequence,
                    event_type=RuntimeEventType.usage_updated,
                    stage=stage,
                    thread_id=thread_id,
                    turn_id=str(turn_handle.id),
                    safe_message="Model usage was updated.",
                    input_tokens=(
                        input_tokens if isinstance(input_tokens, int) else None
                    ),
                    output_tokens=(
                        output_tokens if isinstance(output_tokens, int) else None
                    ),
                )
                continue

            if method == "turn/completed":
                completed_turn = getattr(payload, "turn", None)
                completed_status = getattr(completed_turn, "status", "failed")
                completed_status_value = getattr(
                    completed_status,
                    "value",
                    completed_status,
                )
                event_sequence += 1
                self._emit_runtime_event(
                    event_sequence=event_sequence,
                    event_type=(
                        RuntimeEventType.turn_completed
                        if completed_status_value == "completed"
                        else RuntimeEventType.turn_failed
                    ),
                    stage=stage,
                    thread_id=thread_id,
                    turn_id=str(turn_handle.id),
                    safe_message=(
                        "Model stage completed."
                        if completed_status_value == "completed"
                        else "Model stage failed."
                    ),
                )

        if completed_turn is None:
            raise RuntimeError("The Codex stream ended without turn completion.")
        return _StreamedTurnResult(
            id=str(getattr(completed_turn, "id", turn_handle.id)),
            status=getattr(completed_turn, "status", "failed"),
            final_response=final_response,
            usage=token_usage,
        )

    def _emit_runtime_event(
        self,
        *,
        event_sequence: int,
        event_type: RuntimeEventType,
        stage: str,
        thread_id: str,
        turn_id: str,
        safe_message: str,
        tool_call_id: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        """Emit one bounded event with no raw SDK payload or provider identity."""

        if self._event_sink is None:
            return
        event_material = (
            f"{thread_id}\n{turn_id}\n{event_sequence}\n{event_type.value}"
        ).encode()
        self._event_sink(
            RuntimeEvent(
                event_id=f"event-{sha256(event_material).hexdigest()[:24]}",
                event_type=event_type,
                stage=stage,
                safe_message=safe_message,
                tool_call_id=tool_call_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        )
