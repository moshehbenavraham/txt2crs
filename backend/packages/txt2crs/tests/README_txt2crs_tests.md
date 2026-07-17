# txt2crs Library Tests

The reusable library keeps its tests beside its package metadata so the test
suite remains available when the library is exported independently.

- `unit/` verifies deterministic domain and application behavior.
- `contract/` verifies ports implemented by AI, research, persistence, and
  rendering adapters.
- `integration/` verifies independently useful adapters against controlled
  local or fake external systems.
- `acceptance/` contains explicitly enabled live subscription checks.

Every behavior test is written before the corresponding implementation. Live
provider tests must be explicitly marked and excluded from the default suite.
The normal suite uses deterministic fakes, local SQLite, private temporary
artifact roots, and `httpx` mock transports, so it requires no credentials or
network access. It also verifies real DOCX/PDF parsing, per-module checkpoint
resume, rolling admission quotas, retention deletion, and distribution
resources.
