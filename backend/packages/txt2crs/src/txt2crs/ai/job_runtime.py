# SPDX-License-Identifier: MIT-0

"""Fresh per-job state and owned provider-session resources.

Mutable counters, cancellation flags, temporary files, clients, listeners,
and provider processes must belong to exactly one execution attempt. This
module centralizes that ownership so neither the application shell nor the
generation pipeline has to remember a partial cleanup sequence.
"""

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, Protocol

from txt2crs.ai.budgets import RunBudget, RunBudgetLimits
from txt2crs.ai.codex_runtime import CodexRuntime
from txt2crs.ai.model_policy import ExactModelPolicy
from txt2crs.ai.runtime import CancellationToken, CodexAdapter
from txt2crs.ai.runtime_status import RuntimeReadinessStatus
from txt2crs.jobs.requests import ExecutionProfile


class CloseableCodexAdapter(CodexAdapter, Protocol):
    """Codex adapter whose process/client resources have explicit ownership."""

    def close(self) -> None:
        """Release the SDK client and its managed app-server process."""


class ProviderSessionCleanupError(RuntimeError):
    """A managed provider resource failed to close without a primary error."""


class ProviderSessionReadinessError(RuntimeError):
    """The complete managed provider graph is not ready for job execution."""


def _enter_owned_context[ContextValue](
    *,
    resource_stack: ExitStack,
    resource_context: AbstractContextManager[ContextValue],
    safe_resource_name: str,
) -> ContextValue:
    """Enter one context and preserve primary errors during its cleanup."""

    resource_value = resource_context.__enter__()

    def close_resource_preserving_primary_error(
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        """Exit one dependency without exposing or prioritizing cleanup details."""

        try:
            resource_context.__exit__(
                exception_type,
                exception_value,
                traceback,
            )
        except Exception:
            if exception_value is None:
                raise ProviderSessionCleanupError(
                    f"The managed {safe_resource_name} resource failed to close."
                ) from None
            exception_value.add_note(
                f"The managed {safe_resource_name} resource also failed to close."
            )
        return False

    resource_stack.push(close_resource_preserving_primary_error)
    return resource_value


@dataclass(frozen=True, slots=True)
class JobRuntimeResources:
    """Fresh mutable accounting and cancellation state for one job attempt."""

    budget: RunBudget
    cancellation: CancellationToken


class JobRuntimeResourcesFactory:
    """Build pristine resource state from an accepted execution profile."""

    def create(self, execution_profile: ExecutionProfile) -> JobRuntimeResources:
        """Return new counters and a new cancellation token every time."""

        # Spell the mapping out so a future request-field addition cannot
        # silently flow into RunBudgetLimits or be accidentally omitted.
        run_limits = execution_profile.run_limits
        budget_limits = RunBudgetLimits(
            maximum_turns=run_limits.maximum_turns,
            maximum_research_calls=run_limits.maximum_research_calls,
            maximum_search_calls=run_limits.maximum_search_calls,
            maximum_extract_calls=run_limits.maximum_extract_calls,
            maximum_sources=run_limits.maximum_sources,
            maximum_extracted_bytes=run_limits.maximum_extracted_bytes,
            maximum_input_tokens=run_limits.maximum_input_tokens,
            maximum_output_tokens=run_limits.maximum_output_tokens,
            maximum_retries=run_limits.maximum_retries,
            maximum_repairs=run_limits.maximum_repairs,
            maximum_elapsed_seconds=run_limits.maximum_elapsed_seconds,
        )
        return JobRuntimeResources(
            budget=RunBudget(budget_limits),
            cancellation=CancellationToken(),
        )


@dataclass(frozen=True, slots=True)
class ManagedProviderSession:
    """Values available only while the complete provider stack is open."""

    resources: JobRuntimeResources
    worker_directory: Path
    http_client: Any
    research_mcp: Any
    adapter: CloseableCodexAdapter
    runtime: CodexRuntime


class ManagedProviderSessionFactory:
    """Open temporary, HTTP, MCP, and Codex resources in dependency order."""

    def __init__(
        self,
        *,
        temporary_worker_context_factory: Callable[[], AbstractContextManager[Path]],
        http_client_context_factory: Callable[[], AbstractContextManager[Any]],
        research_mcp_context_factory: Callable[
            [JobRuntimeResources, Any],
            AbstractContextManager[Any],
        ],
        codex_adapter_factory: Callable[
            [Path, Any],
            CloseableCodexAdapter,
        ],
        model_policy: ExactModelPolicy,
    ) -> None:
        self._temporary_worker_context_factory = temporary_worker_context_factory
        self._http_client_context_factory = http_client_context_factory
        self._research_mcp_context_factory = research_mcp_context_factory
        self._codex_adapter_factory = codex_adapter_factory
        self._model_policy = model_policy

    @contextmanager
    def open(
        self,
        resources: JobRuntimeResources,
    ) -> Iterator[ManagedProviderSession]:
        """Yield a complete session and unwind every partial state in reverse."""

        with ExitStack() as resource_stack:
            worker_directory = _enter_owned_context(
                resource_stack=resource_stack,
                resource_context=self._temporary_worker_context_factory(),
                safe_resource_name="temporary worker",
            )
            http_client = _enter_owned_context(
                resource_stack=resource_stack,
                resource_context=self._http_client_context_factory(),
                safe_resource_name="HTTP client",
            )
            research_mcp = _enter_owned_context(
                resource_stack=resource_stack,
                resource_context=self._research_mcp_context_factory(
                    resources,
                    http_client,
                ),
                safe_resource_name="research MCP",
            )
            adapter = self._codex_adapter_factory(
                worker_directory,
                research_mcp,
            )

            def close_adapter_preserving_primary_error(
                exception_type: type[BaseException] | None,
                exception_value: BaseException | None,
                traceback: TracebackType | None,
            ) -> Literal[False]:
                """Close Codex first without masking an existing job failure."""

                del exception_type, traceback
                try:
                    adapter.close()
                except Exception:
                    if exception_value is None:
                        raise ProviderSessionCleanupError(
                            "The managed Codex adapter failed to close."
                        ) from None
                    exception_value.add_note(
                        "The managed Codex adapter also failed to close."
                    )
                return False

            # Register after construction succeeds. ExitStack invokes this
            # before the earlier MCP/HTTP/temporary context exits.
            resource_stack.push(close_adapter_preserving_primary_error)
            runtime = CodexRuntime(
                adapter=adapter,
                model_policy=self._model_policy,
            )
            if runtime.inspect_readiness().status is not RuntimeReadinessStatus.ready:
                raise ProviderSessionReadinessError(
                    "The managed provider session is not ready."
                )
            yield ManagedProviderSession(
                resources=resources,
                worker_directory=worker_directory,
                http_client=http_client,
                research_mcp=research_mcp,
                adapter=adapter,
                runtime=runtime,
            )
