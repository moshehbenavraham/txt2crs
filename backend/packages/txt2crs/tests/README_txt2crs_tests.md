# txt2crs Library Tests

The reusable library keeps its tests beside its package metadata so the test
suite remains available when the library is exported independently.

- `unit/` verifies deterministic domain and application behavior.
- `contract/` verifies ports implemented by AI, research, persistence, and
  rendering adapters.
- `integration/` verifies independently useful adapters against controlled
  local or fake external systems.

Every behavior test is written before the corresponding implementation. Live
provider tests must be explicitly marked and excluded from the default suite.
