# SPDX-License-Identifier: MIT-0

"""Distribution provenance tests for materially adapted donor behavior."""

from pathlib import Path


def test_hermes_adaptations_ship_notice_commit_and_mit_spdx() -> None:
    """Adapted files and the distribution retain the reviewed MIT provenance."""

    package_root = Path(__file__).resolve().parents[2]
    notice = (package_root / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    donor_revision = "0f102fa4dc04b7dfdab048169aaaa640d09d7523"

    assert "Nous Research" in notice
    assert donor_revision in notice
    for relative_path in (
        "src/txt2crs/ai/retry.py",
        "src/txt2crs/ai/tool_guardrails.py",
        "src/txt2crs/research/tavily.py",
        "src/txt2crs/security/url_safety.py",
    ):
        source_text = (package_root / relative_path).read_text(encoding="utf-8")
        assert source_text.startswith("# SPDX-License-Identifier: MIT\n")
        assert donor_revision in source_text
