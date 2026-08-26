# txt2crs Package Documentation

This folder contains the requirements and implementation research that directly
guide the txt2crs Python package:

- [AI usage needs](AI_USAGE_NEEDS.md)
- [Hermes minimum code-pull evaluation](HERMES_MINIMUM_CODE_PULL_EVALUATION.md)
- [AIOS runtime supplement](AIOS_RUNTIME_SUPPLEMENT.md)
- [Package implementation compliance](IMPLEMENTATION_COMPLIANCE.md)
- [Pinned Codex app-server protocol fixtures](fixtures/README_fixtures.md)

The implementation now covers the documented minimum package boundary:
Codex execution through either ChatGPT or Platform API credentials, a two-tool
loopback research MCP service, source/evidence provenance, strict educational contracts, 16-artifact
multi-format rendering, per-stage durable resume, private retained storage,
spend admission, safety gates, private evaluations, and donor-independent
builds. Older requirement studies in this folder describe the original Build
Week constraints and are retained as design history; this index and the
implementation compliance matrix describe the current product. The FastAPI
application shell remains responsible for browser
authentication, HTTP routes, payment, provider-specific notifications, and
user experience.

Project-level documentation remains in the repository's
[`docs/` folder](https://github.com/moshehbenavraham/txt2crs/tree/main/docs).
