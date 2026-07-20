# Codex Protocol Fixtures

`codex_app_server_0.144.4/` was generated from the exact locked
`openai-codex-cli-bin==0.144.4` executable with:

```bash
codex app-server generate-json-schema --experimental --out <directory>
```

The fixture is an upgrade guard for account, model, turn, interrupt, MCP tool,
event, output-schema, usage, and rate-limit protocol shapes. Change it only as
part of a deliberate SDK/runtime upgrade with contract-test review.
