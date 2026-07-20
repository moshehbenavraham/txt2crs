# Backend Application Tests

This directory contains tests for the FastAPI application shell and
product-level acceptance behavior.

Core tests cover authentication, users, durable course jobs, configuration,
middleware, health, migrations, the local admin MCP, and application
services. The `acceptance/` suite proves authenticated end-to-end generation,
recovery, delivery, and engine-first account erasure through the real public
facade. Engine unit, contract, acceptance, and adapter integration tests
remain under `backend/packages/txt2crs/tests/`.
