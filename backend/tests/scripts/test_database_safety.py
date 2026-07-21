from pydantic import PostgresDsn
from sqlalchemy.engine import make_url

from tests.database_safety import require_isolated_test_database


def test_database_guard_accepts_only_explicit_test_database_names() -> None:
    """Destructive fixtures require a visibly isolated database name."""

    require_isolated_test_database(
        make_url("postgresql+psycopg://user:secret@localhost:5450/app_test")
    )
    require_isolated_test_database(
        make_url("postgresql+psycopg://user:secret@localhost:5450/test_app")
    )
    require_isolated_test_database(
        PostgresDsn("postgresql+psycopg://user:secret@localhost:5450/app_test")
    )


def test_database_guard_rejects_live_names_without_exposing_credentials() -> None:
    """The refusal explains the fix while keeping the URL password private."""

    try:
        require_isolated_test_database(
            make_url("postgresql+psycopg://user:private-value@db:5432/app")
        )
    except RuntimeError as error:
        message = str(error)
    else:
        raise AssertionError("The live database name must be rejected.")

    assert "app_test" in message
    assert "private-value" not in message
