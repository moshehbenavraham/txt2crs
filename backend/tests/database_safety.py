"""Fail-closed guard for destructive application database fixtures."""

from pydantic import PostgresDsn
from sqlalchemy.engine import URL, make_url


def require_isolated_test_database(database_url: URL | PostgresDsn) -> None:
    """Reject a database whose name does not visibly identify test isolation.

    The application suite deletes shell-owned rows during cleanup. Requiring a
    name such as ``app_test`` or ``test_app`` prevents an accidental run
    against the durable local Compose database before any connection opens.
    """

    # Settings exposes a Pydantic DSN while migration helpers commonly expose
    # SQLAlchemy URLs. Normalize both through SQLAlchemy's non-connecting URL
    # parser so this guard remains a pure preflight check.
    parsed_database_url = (
        database_url if isinstance(database_url, URL) else make_url(str(database_url))
    )
    database_name = parsed_database_url.database or ""
    normalized_database_name = database_name.lower()
    is_explicit_test_database = normalized_database_name.startswith(
        "test_"
    ) or normalized_database_name.endswith("_test")
    if is_explicit_test_database:
        return

    raise RuntimeError(
        "Backend tests refused a non-test application database. "
        "Create an isolated database and set POSTGRES_DB to an explicit test "
        "name such as app_test before running pytest."
    )


def main() -> None:
    """Validate configured database safety for shell test entrypoints."""

    from app.core.config import settings

    require_isolated_test_database(settings.SQLALCHEMY_DATABASE_URI)


if __name__ == "__main__":
    main()
