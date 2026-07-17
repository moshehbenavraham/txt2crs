# SPDX-License-Identifier: MIT-0

"""Dry-run planning, private atomic snapshots, and aggregate publication."""

import json
import os
import re
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path

from txt2crs.evals.models import (
    EvaluationCase,
    EvaluationPlan,
    EvaluationResult,
    PublishedEvaluationAggregate,
)

_SAFE_COMPONENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


class SnapshotPathError(ValueError):
    """An evaluation identifier could escape the private snapshot root."""


class EvaluationSnapshotStore:
    """Write/read private case snapshots atomically beneath one root."""

    def __init__(self, root_directory: Path) -> None:
        self._root_directory = root_directory.resolve()
        self._root_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._root_directory.chmod(0o700)

    def _snapshot_path(self, case_id: str, case_version: str) -> Path:
        """Build and verify a confined path from safe identifier components."""

        for component in (case_id, case_version):
            if _SAFE_COMPONENT_PATTERN.fullmatch(component) is None:
                raise SnapshotPathError("Evaluation snapshot identifier is unsafe.")
        candidate_path = (
            self._root_directory / case_id / f"{case_version}.json"
        ).resolve()
        if not candidate_path.is_relative_to(self._root_directory):
            raise SnapshotPathError("Evaluation snapshot path escaped its root.")
        return candidate_path

    def write(self, result: EvaluationResult) -> Path:
        """Atomically persist one immutable private result with mode 0600."""

        snapshot_path = self._snapshot_path(result.case_id, result.case_version)
        snapshot_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary_path = snapshot_path.with_suffix(".json.tmp")
        serialized_result = json.dumps(
            result.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        temporary_path.write_text(serialized_result, encoding="utf-8")
        temporary_path.chmod(0o600)
        os.replace(temporary_path, snapshot_path)
        snapshot_path.chmod(0o600)
        return snapshot_path

    def read(self, case_id: str, case_version: str) -> EvaluationResult:
        """Read and validate one private result."""

        snapshot_path = self._snapshot_path(case_id, case_version)
        return EvaluationResult.model_validate_json(
            snapshot_path.read_text(encoding="utf-8")
        )


class EvaluationRunner:
    """Plan before spending and execute only on explicit live runs."""

    def __init__(
        self,
        *,
        execute_case: Callable[[EvaluationCase], EvaluationResult],
    ) -> None:
        self._execute_case = execute_case

    def plan(
        self,
        *,
        cases: list[EvaluationCase],
        model_id: str,
        maximum_turns: int,
        live: bool,
    ) -> EvaluationPlan:
        """Return scope only; planning never calls the provider."""

        return EvaluationPlan(
            schema_version="1.0",
            case_ids=[case.case_id for case in cases],
            model_id=model_id,
            maximum_turns=maximum_turns,
            live=live,
        )

    def run(
        self,
        *,
        cases: list[EvaluationCase],
        live: bool,
    ) -> list[EvaluationResult]:
        """Execute cases only after explicit live confirmation."""

        if not live:
            return []
        return [self._execute_case(case) for case in cases]

    @staticmethod
    def publish_aggregate(
        results: list[EvaluationResult],
    ) -> PublishedEvaluationAggregate:
        """Publish counts/rates only, never private case-level content."""

        rubric_values: dict[str, list[float]] = defaultdict(list)
        invariant_values: dict[str, list[bool]] = defaultdict(list)
        for result in results:
            for rubric_name, rubric_score in result.rubric_scores.items():
                rubric_values[rubric_name].append(rubric_score)
            for invariant_name, invariant_passed in result.invariant_results.items():
                invariant_values[invariant_name].append(invariant_passed)
        case_count = len(results)
        passed_count = sum(result.passed for result in results)
        return PublishedEvaluationAggregate(
            schema_version="1.0",
            case_count=case_count,
            passed_count=passed_count,
            pass_rate=passed_count / case_count if case_count else 0,
            mean_rubric_scores={
                rubric_name: sum(values) / len(values)
                for rubric_name, values in sorted(rubric_values.items())
            },
            invariant_pass_rates={
                invariant_name: sum(values) / len(values)
                for invariant_name, values in sorted(invariant_values.items())
            },
        )
