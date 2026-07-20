# SPDX-License-Identifier: MIT-0

"""Upgrade guard for the exact pinned Codex app-server protocol."""

import json
import tomllib
from importlib.resources import files
from pathlib import Path

_REQUIRED_CODEX_RUNTIME_VERSION = "0.144.4"


def test_pinned_protocol_fixture_covers_runtime_methods_and_events() -> None:
    """Account, model, turn, MCP, usage, and interrupt shapes stay reviewable."""

    package_root = Path(__file__).resolve().parents[2]
    schema_path = (
        package_root
        / "docs"
        / "fixtures"
        / f"codex_app_server_{_REQUIRED_CODEX_RUNTIME_VERSION}"
        / "codex_app_server_protocol.v2.schemas.json"
    )
    protocol_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    serialized_schema = json.dumps(protocol_schema, separators=(",", ":"))

    assert protocol_schema["title"] == "CodexAppServerProtocolV2"
    for required_protocol_term in (
        "account/read",
        "model/list",
        "turn/start",
        "turn/interrupt",
        "mcpToolCall",
        "thread/tokenUsage/updated",
    ):
        assert required_protocol_term in serialized_schema


def test_sdk_and_bundled_runtime_are_pinned_to_reviewed_sol_release() -> None:
    """The packaged runtime must not predate the reviewed GPT-5.6 catalog."""

    package_root = Path(__file__).resolve().parents[2]
    package_configuration = tomllib.loads(
        (package_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    dependencies = package_configuration["project"]["dependencies"]

    assert f"openai-codex=={_REQUIRED_CODEX_RUNTIME_VERSION}" in dependencies
    assert f"openai-codex-cli-bin=={_REQUIRED_CODEX_RUNTIME_VERSION}" in dependencies


def test_evaluation_resources_remain_importable_with_protocol_test_installed() -> None:
    """Resource loading used by wheels remains independent from repository docs."""

    assert files("txt2crs.evals").joinpath("fixtures", "short_prompt.txt").is_file()
