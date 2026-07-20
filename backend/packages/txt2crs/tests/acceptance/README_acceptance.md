# txt2crs Live Acceptance Tests

Live tests are disabled by default because they use the dedicated ChatGPT
subscription. From the repository root, bootstrap that identity with the short
helper; no separately installed Codex CLI is required:

```bash
./scripts/auth-codex.sh
```

## Small subscription and MCP probe

This inexpensive probe uses deterministic local research data. It proves the
saved ChatGPT account, one exact reviewed model, the loopback MCP boundary,
schema validation, safe events, and subscription usage accounting. It is not a
representative course and does not call Tavily.

Run it from `backend/` against the resulting app-owned credential directory:

```bash
TXT2CRS_RUN_LIVE_CODEX=1 \
TXT2CRS_MODEL_ID=gpt-5.6-sol \
TXT2CRS_LIVE_CODEX_HOME="$PWD/../.txt2crs-system/codex-home" \
uv run --package txt2crs pytest \
  packages/txt2crs/tests/acceptance -m live
```

`TXT2CRS_MODEL_ID` can select one reviewed model. The test starts a loopback
research server with deterministic data, verifies ChatGPT account mode, runs a
schema turn that must call the allowlisted research tool, captures safe stream
events and usage, and interrupts no external application state.

## Representative full-course gate

The release proof is a separate, explicitly enabled test. It pins
`gpt-5.6-sol`, reads the private Tavily key through the root `.env`, submits one
synthetic DNS-education topic through `RealApplicationFactory`, observes
durable checkpoints, and downloads all sixteen owner-private artifacts. Reusing
the same state directory and idempotency key resumes or replays the same job
instead of creating duplicate paid work.

Run this gate exactly once from `backend/` after the aggregate application
readiness check passes:

```bash
TXT2CRS_RUN_LIVE_COURSE=1 \
TXT2CRS_LIVE_STATE_ROOT="$PWD/../.txt2crs-system/live-course" \
TXT2CRS_LIVE_CODEX_HOME="$PWD/../.txt2crs-system/codex-home" \
uv run --env-file ../.env --package txt2crs pytest \
  packages/txt2crs/tests/acceptance/test_live_codex_subscription.py::test_live_application_delivers_one_researched_course \
  -m live -s -v
```

Never add the Tavily key to the command, test output, or tracked evidence. The
full-course gate records only bounded model-family, checkpoint-count, duration,
artifact-count, hash, and size facts; raw prompts, provider payloads, artifact
bodies, identifiers, and private paths remain outside release evidence.
