# txt2crs Live Acceptance Tests

The live test is disabled by default because it uses an authenticated ChatGPT
subscription. Run it only with a dedicated test identity:

```bash
TXT2CRS_RUN_LIVE_CODEX=1 \
TXT2CRS_LIVE_CODEX_HOME=/path/to/isolated/codex-home \
uv run --package txt2crs pytest \
  packages/txt2crs/tests/acceptance -m live
```

`TXT2CRS_LIVE_MODEL` can select one entitled model. The test starts a loopback
research server with deterministic data, verifies ChatGPT account mode, runs a
schema turn that must call the allowlisted research tool, captures safe stream
events and usage, and interrupts no external application state.
