# Backend Application Tests

This directory contains tests for the FastAPI application shell and
product-level acceptance behavior.

Core tests cover authentication, users, items, configuration, middleware,
health, migrations, and application services. The `acceptance/` suite is the
home for authenticated end-to-end generation, recovery, delivery, and
frontend-facing behavior as those routes are composed. Engine unit, contract,
acceptance, and adapter integration tests remain under
`backend/packages/txt2crs/tests/`.
