"""Static regressions for mixed-stack quality workflow coverage."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
QUALITY_WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "quality.yml"
STANDALONE_BACKEND_WORKFLOW = (
    REPOSITORY_ROOT / ".github" / "workflows" / "test-backend.yml"
)
BACKEND_LINT_SCRIPT = REPOSITORY_ROOT / "backend" / "scripts" / "lint.sh"


def test_quality_workflow_validates_the_reusable_engine_package() -> None:
    """The shell's green status must include its separately configured engine."""

    workflow_text = QUALITY_WORKFLOW.read_text(encoding="utf-8")

    assert "validate-engine:" in workflow_text
    assert "uv run --package txt2crs ruff check ." in workflow_text
    assert "uv run --package txt2crs mypy" in workflow_text
    assert "uv run --package txt2crs pytest -q" in workflow_text
    assert "- validate-engine" in workflow_text


def test_backend_lint_checks_authored_tests_as_well_as_application_code() -> None:
    """A malformed regression test must fail CI before the test runner starts."""

    lint_script_text = BACKEND_LINT_SCRIPT.read_text(encoding="utf-8")

    assert "ruff check app tests" in lint_script_text
    assert "ruff format app tests --check" in lint_script_text


def test_backend_coverage_gates_match_the_measured_phase_baseline() -> None:
    """Coverage gates should prevent regressions without claiming 90% coverage."""

    quality_workflow_text = QUALITY_WORKFLOW.read_text(encoding="utf-8")
    standalone_workflow_text = STANDALONE_BACKEND_WORKFLOW.read_text(encoding="utf-8")

    assert "coverage report --fail-under=78" in quality_workflow_text
    assert "coverage report --fail-under=78" in standalone_workflow_text
    assert "--fail-under=85" not in quality_workflow_text
    assert "--fail-under=90" not in standalone_workflow_text
