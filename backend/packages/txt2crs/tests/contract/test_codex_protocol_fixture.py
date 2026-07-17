# SPDX-License-Identifier: MIT-0

"""Upgrade guard for the exact pinned Codex app-server protocol."""

import json
from importlib.resources import files
from pathlib import Path


def test_pinned_protocol_fixture_covers_runtime_methods_and_events() -> None:
    """Account, model, turn, MCP, usage, and interrupt shapes stay reviewable."""

    package_root = Path(__file__).resolve().parents[2]
    schema_path = (
        package_root
        / "docs"
        / "fixtures"
        / "codex_app_server_0.137.0a4"
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


def test_evaluation_resources_remain_importable_with_protocol_test_installed() -> None:
    """Resource loading used by wheels remains independent from repository docs."""

    assert files("txt2crs.evals").joinpath("fixtures", "short_prompt.txt").is_file()
