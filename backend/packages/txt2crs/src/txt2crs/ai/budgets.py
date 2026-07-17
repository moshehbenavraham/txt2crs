# SPDX-License-Identifier: MIT-0

"""Thread-safe hard limits for one course-generation job.

The counter shape was informed by Hermes' small iteration-budget helper, but
this implementation is local to txt2crs and covers every scarce resource in
the education workflow. A reservation happens *before* work begins so parallel
workers cannot overspend and discover the problem afterward.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields
from threading import Lock
from time import monotonic


class BudgetExceededError(RuntimeError):
    """Raised before an operation would cross a configured hard limit."""

    def __init__(self, resource_name: str, limit: int | float) -> None:
        self.resource_name = resource_name
        self.limit = limit
        super().__init__(f"The {resource_name} budget limit ({limit}) is exhausted.")


@dataclass(frozen=True, slots=True)
class RunBudgetLimits:
    """Maximum resource use allowed for one complete generation job."""

    maximum_turns: int
    maximum_research_calls: int
    maximum_search_calls: int
    maximum_extract_calls: int
    maximum_sources: int
    maximum_extracted_bytes: int
    maximum_input_tokens: int
    maximum_output_tokens: int
    maximum_retries: int
    maximum_repairs: int
    maximum_elapsed_seconds: float

    def __post_init__(self) -> None:
        """Reject unusable limits when configuration is loaded."""

        for configured_field in fields(self):
            field_name = configured_field.name
            configured_limit = getattr(self, field_name)
            if configured_limit <= 0:
                raise ValueError(f"{field_name} must be greater than zero.")


@dataclass(frozen=True, slots=True)
class RunBudgetSnapshot:
    """Immutable counters safe to persist with a job checkpoint."""

    turns: int = 0
    research_calls: int = 0
    search_calls: int = 0
    extract_calls: int = 0
    sources: int = 0
    extracted_bytes: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    retries: int = 0
    repairs: int = 0
    elapsed_seconds: float = 0


class RunBudget:
    """Reserve and report job resources without concurrency races."""

    def __init__(
        self,
        limits: RunBudgetLimits,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.limits = limits
        self._clock = clock
        self._started_at = clock()
        self._restored = False
        self._lock = Lock()
        self._turns = 0
        self._research_calls = 0
        self._search_calls = 0
        self._extract_calls = 0
        self._sources = 0
        self._extracted_bytes = 0
        self._input_tokens = 0
        self._output_tokens = 0
        self._retries = 0
        self._repairs = 0

    def restore(self, snapshot: RunBudgetSnapshot) -> None:
        """Restore one durable snapshot into a fresh worker budget.

        Restoration is intentionally one-shot and requires pristine counters.
        Otherwise a caller could accidentally double-count or, worse, replace
        work already reserved by the current process.
        """

        counter_values = {
            "turns": snapshot.turns,
            "research_calls": snapshot.research_calls,
            "search_calls": snapshot.search_calls,
            "extract_calls": snapshot.extract_calls,
            "sources": snapshot.sources,
            "extracted_bytes": snapshot.extracted_bytes,
            "input_tokens": snapshot.input_tokens,
            "output_tokens": snapshot.output_tokens,
            "retries": snapshot.retries,
            "repairs": snapshot.repairs,
        }
        if any(value < 0 for value in counter_values.values()):
            raise ValueError("Budget snapshot counters cannot be negative.")
        configured_limits = {
            "turns": self.limits.maximum_turns,
            "research_calls": self.limits.maximum_research_calls,
            "search_calls": self.limits.maximum_search_calls,
            "extract_calls": self.limits.maximum_extract_calls,
            "sources": self.limits.maximum_sources,
            "extracted_bytes": self.limits.maximum_extracted_bytes,
            "input_tokens": self.limits.maximum_input_tokens,
            "output_tokens": self.limits.maximum_output_tokens,
            "retries": self.limits.maximum_retries,
            "repairs": self.limits.maximum_repairs,
        }
        for resource_name, restored_value in counter_values.items():
            if restored_value > configured_limits[resource_name]:
                raise BudgetExceededError(
                    resource_name,
                    configured_limits[resource_name],
                )
        if snapshot.research_calls != snapshot.search_calls + snapshot.extract_calls:
            raise ValueError(
                "Research-call total must equal search and extract calls."
            )
        if (
            snapshot.elapsed_seconds < 0
            or snapshot.elapsed_seconds > self.limits.maximum_elapsed_seconds
        ):
            raise BudgetExceededError(
                "elapsed_seconds",
                self.limits.maximum_elapsed_seconds,
            )

        with self._lock:
            current_values = (
                self._turns,
                self._research_calls,
                self._search_calls,
                self._extract_calls,
                self._sources,
                self._extracted_bytes,
                self._input_tokens,
                self._output_tokens,
                self._retries,
                self._repairs,
            )
            if self._restored or any(current_values):
                raise RuntimeError(
                    "Budget counters were already restored or reserved."
                )
            self._turns = snapshot.turns
            self._research_calls = snapshot.research_calls
            self._search_calls = snapshot.search_calls
            self._extract_calls = snapshot.extract_calls
            self._sources = snapshot.sources
            self._extracted_bytes = snapshot.extracted_bytes
            self._input_tokens = snapshot.input_tokens
            self._output_tokens = snapshot.output_tokens
            self._retries = snapshot.retries
            self._repairs = snapshot.repairs
            self._started_at = self._clock() - snapshot.elapsed_seconds
            self._restored = True

    def _check_elapsed_time(self) -> float:
        """Return elapsed time and fail if the job deadline has passed."""

        elapsed_seconds = max(0.0, self._clock() - self._started_at)
        if elapsed_seconds > self.limits.maximum_elapsed_seconds:
            raise BudgetExceededError(
                "elapsed_seconds",
                self.limits.maximum_elapsed_seconds,
            )
        return elapsed_seconds

    def _reserve_counter(
        self,
        *,
        attribute_name: str,
        resource_name: str,
        amount: int,
        maximum: int,
    ) -> None:
        """Atomically add a positive amount without crossing ``maximum``."""

        if amount < 0:
            raise ValueError(f"{resource_name} reservation cannot be negative.")

        with self._lock:
            self._check_elapsed_time()
            current_amount = int(getattr(self, attribute_name))
            if current_amount + amount > maximum:
                raise BudgetExceededError(resource_name, maximum)
            setattr(self, attribute_name, current_amount + amount)

    def reserve_turn(self) -> None:
        """Reserve one model turn."""

        self._reserve_counter(
            attribute_name="_turns",
            resource_name="turns",
            amount=1,
            maximum=self.limits.maximum_turns,
        )

    def reserve_research_call(self, *, tool_name: str) -> None:
        """Atomically reserve one call for an allowlisted research tool."""

        tool_counter_and_limit = {
            "research_search": ("_search_calls", self.limits.maximum_search_calls),
            "research_extract": ("_extract_calls", self.limits.maximum_extract_calls),
        }
        if tool_name not in tool_counter_and_limit:
            raise ValueError(f"Unknown research tool: {tool_name}")

        tool_counter_name, tool_limit = tool_counter_and_limit[tool_name]
        with self._lock:
            self._check_elapsed_time()
            if self._research_calls + 1 > self.limits.maximum_research_calls:
                raise BudgetExceededError(
                    "research_calls",
                    self.limits.maximum_research_calls,
                )
            current_tool_calls = int(getattr(self, tool_counter_name))
            if current_tool_calls + 1 > tool_limit:
                raise BudgetExceededError(f"{tool_name}_calls", tool_limit)
            self._research_calls += 1
            setattr(self, tool_counter_name, current_tool_calls + 1)

    def reserve_sources(self, source_count: int) -> None:
        """Reserve source-ledger entries before accepting search results."""

        self._reserve_counter(
            attribute_name="_sources",
            resource_name="sources",
            amount=source_count,
            maximum=self.limits.maximum_sources,
        )

    def reserve_extracted_bytes(self, byte_count: int) -> None:
        """Reserve bytes before persisting extracted source content."""

        self._reserve_counter(
            attribute_name="_extracted_bytes",
            resource_name="extracted_bytes",
            amount=byte_count,
            maximum=self.limits.maximum_extracted_bytes,
        )

    def record_tokens(self, *, input_tokens: int, output_tokens: int) -> None:
        """Record provider-reported tokens while preserving separate limits."""

        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token counts cannot be negative.")

        with self._lock:
            self._check_elapsed_time()
            if self._input_tokens + input_tokens > self.limits.maximum_input_tokens:
                raise BudgetExceededError(
                    "input_tokens",
                    self.limits.maximum_input_tokens,
                )
            if self._output_tokens + output_tokens > self.limits.maximum_output_tokens:
                raise BudgetExceededError(
                    "output_tokens",
                    self.limits.maximum_output_tokens,
                )
            self._input_tokens += input_tokens
            self._output_tokens += output_tokens

    def ensure_token_capacity(self, *, estimated_input_tokens: int) -> None:
        """Preflight an estimated prompt without claiming it as reported usage."""

        if estimated_input_tokens < 0:
            raise ValueError("Estimated input tokens cannot be negative.")
        with self._lock:
            self._check_elapsed_time()
            if (
                self._input_tokens + estimated_input_tokens
                > self.limits.maximum_input_tokens
            ):
                raise BudgetExceededError(
                    "input_tokens",
                    self.limits.maximum_input_tokens,
                )

    def reserve_retry(self) -> None:
        """Reserve one retry after a classified transient failure."""

        self._reserve_counter(
            attribute_name="_retries",
            resource_name="retries",
            amount=1,
            maximum=self.limits.maximum_retries,
        )

    def reserve_repair(self) -> None:
        """Reserve one model repair after deterministic validation fails."""

        self._reserve_counter(
            attribute_name="_repairs",
            resource_name="repairs",
            amount=1,
            maximum=self.limits.maximum_repairs,
        )

    def snapshot(self) -> RunBudgetSnapshot:
        """Return counters and current elapsed time under one lock."""

        with self._lock:
            elapsed_seconds = self._check_elapsed_time()
            return RunBudgetSnapshot(
                turns=self._turns,
                research_calls=self._research_calls,
                search_calls=self._search_calls,
                extract_calls=self._extract_calls,
                sources=self._sources,
                extracted_bytes=self._extracted_bytes,
                input_tokens=self._input_tokens,
                output_tokens=self._output_tokens,
                retries=self._retries,
                repairs=self._repairs,
                elapsed_seconds=elapsed_seconds,
            )
