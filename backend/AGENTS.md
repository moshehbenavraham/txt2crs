# Backend AGENTS.md

## Quick Reference

| Purpose | Location |
|---------|----------|
| Entry point | `app/main.py` |
| API routes | `app/api/routes/` |
| Database models | `app/models.py` |
| CRUD operations | `app/crud.py` |
| Schemas | `app/schemas/` |
| Configuration | `app/core/config.py` |
| Error codes | `app/core/constants.py` |
| Custom exceptions | `app/core/exceptions.py` |
| Structured logging | `app/core/logging.py` |
| Security/Auth | `app/core/security.py` |
| Rate limiting | `app/core/rate_limit.py` |

## Adding a New Endpoint

1. **Create/update model** in `app/models.py` (if new table needed)
2. **Add CRUD functions** in `app/crud.py`
3. **Create schemas** in `app/schemas/` for request/response
4. **Create route** in `app/api/routes/`
5. **Register router** in `app/api/main.py`
6. **Run tests**: `POSTGRES_DB=app_test uv run pytest tests/ -v` against a
   separately provisioned and migrated test database
7. **Type check**: `uv run mypy app`

## Database Migrations

```bash
# Generate migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

## Error Handling Pattern

Always use `AppException` with `ErrorCode` for structured errors:

```python
from app.core.constants import ErrorCode
from app.core.exceptions import AppException, NotFoundError

# Generic error
raise AppException(
    code=ErrorCode.USER_NOT_FOUND,
    detail="User with this email does not exist"
)

# Convenience classes
raise NotFoundError(resource="User", identifier=str(user_id))
```

## Logging Pattern

Use structured logging with event naming:

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Event naming: {domain}.{action}_{state}
logger.info("user.create_started")
try:
    user = create_user(session, user_create)
    logger.info("user.create_completed", extra={"user_id": str(user.id)})
except Exception:
    # Keep exception text, email, and other PII out of routine logs.
    logger.error("user.create_failed", extra={"reason_code": "write_failed"})
    raise
```

**Event states**: `_started`, `_completed`, `_failed`, `_validated`, `_rejected`, `_retrying`

## Type Annotations

All functions must have complete type annotations:

```python
from typing import Annotated
from uuid import UUID
from sqlmodel import Session
from app.models import User

def get_user_by_id(
    session: Session,
    user_id: UUID,
) -> User | None:
    """Get user by UUID."""
    return session.get(User, user_id)
```

## Dependency Injection

Use `Annotated` types for FastAPI dependencies:

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.api.deps import get_current_user, get_db
from app.models import User, UserPublic

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
router = APIRouter()

@router.get("/profile", response_model=UserPublic)
def read_profile(current_user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(current_user)
```

## Testing

The shell suite deletes application-owned rows during fixture cleanup. It
fails before connecting unless the configured database name starts with
`test_` or ends with `_test`; never use the normal local `app` database.

```bash
# Run all tests
POSTGRES_DB=app_test uv run pytest tests/ -v

# Run specific test file
POSTGRES_DB=app_test uv run pytest tests/api/test_users.py -v

# Run with coverage
POSTGRES_DB=app_test uv run pytest tests/ --cov=app --cov-report=term-missing

# Run only fast tests (skip slow/integration)
POSTGRES_DB=app_test uv run pytest tests/ -v -m "not slow"
```

## Constants Usage

Always use constants from `app.core.constants`:

```python
from app.core.constants import (
    HTTPStatusCode,
    ErrorCode,
    ErrorMessages,
    Pagination,
    ContentTypes,
)

# HTTP status codes
return Response(status_code=HTTPStatusCode.CREATED)

# Pagination
bounded_limit = min(limit, Pagination.MAX_LIMIT)

# Error messages
detail = ErrorMessages.USER_NOT_FOUND_BY_EMAIL.format(email=email)
```

## API Response Patterns

### Success responses

```python
from fastapi import Depends
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import User, UserPublic, UsersPublic

@router.get(
    "/users",
    response_model=UsersPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_users(session: SessionDep) -> UsersPublic:
    users = session.exec(select(User).limit(100)).all()
    count = session.exec(select(func.count()).select_from(User)).one()
    return UsersPublic(
        data=[UserPublic.model_validate(user) for user in users],
        count=count,
    )
```

### Error responses

```python
from uuid import UUID

from fastapi import Depends

from app.core.exceptions import AppException
from app.core.constants import ErrorCode
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import User, UserPublic

@router.get(
    "/users/{user_id}",
    response_model=UserPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_user(user_id: UUID, session: SessionDep) -> UserPublic:
    user = session.get(User, user_id)
    if not user:
        raise AppException(
            code=ErrorCode.USER_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found",
        )
    return UserPublic.model_validate(user)
```

## Security Notes

- Never log passwords, tokens, or secrets
- Always use parameterized queries (SQLModel handles this)
- Validate all user input with Pydantic
- Check ownership before returning resources
- Rate limiting is enabled in production (see `app/core/rate_limit.py`)
