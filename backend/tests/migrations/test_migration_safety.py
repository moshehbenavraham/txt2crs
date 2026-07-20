from __future__ import annotations

import importlib.util
import re
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from alembic.util import CommandError
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL, make_url

from app.core.config import settings

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "app" / "alembic" / "versions"
BACKEND_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI_PATH = BACKEND_DIR / "alembic.ini"
ALEMBIC_SCRIPT_LOCATION = BACKEND_DIR / "app" / "alembic"
_DB_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _get_alembic_config() -> Config:
    alembic_config = Config(str(ALEMBIC_INI_PATH))
    alembic_config.set_main_option("script_location", str(ALEMBIC_SCRIPT_LOCATION))
    return alembic_config


def _build_admin_database_url() -> URL:
    return make_url(str(settings.SQLALCHEMY_DATABASE_URI)).set(database="postgres")


def _quote_identifier(identifier: str) -> str:
    if not _DB_IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"Unsafe SQL identifier: {identifier}")
    return f'"{identifier}"'


@contextmanager
def _temporary_database() -> Generator[str]:
    db_name = f"migration_roundtrip_{uuid4().hex[:10]}"
    quoted_db_name = _quote_identifier(db_name)
    admin_engine = create_engine(
        _build_admin_database_url(),
        isolation_level="AUTOCOMMIT",
    )
    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE {quoted_db_name}"))
        yield db_name
    finally:
        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :db_name AND pid <> pg_backend_pid()"
                ),
                {"db_name": db_name},
            )
            connection.execute(text(f"DROP DATABASE IF EXISTS {quoted_db_name}"))
        admin_engine.dispose()


@contextmanager
def _use_database(database_name: str) -> Generator[None]:
    original_database_name = settings.POSTGRES_DB
    settings.POSTGRES_DB = database_name
    try:
        yield
    finally:
        settings.POSTGRES_DB = original_database_name


def _assert_item_table_is_absent(database_url: str) -> None:
    """The current application head must contain no donor item table."""

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        assert "user" in inspector.get_table_names()
        assert "item" not in inspector.get_table_names()
    finally:
        engine.dispose()


def _assert_pre_retirement_item_schema(database_url: str) -> None:
    """A one-revision downgrade recreates the complete final donor schema."""

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        columns = {column["name"]: column for column in inspector.get_columns("item")}
        assert set(columns) == {
            "id",
            "title",
            "description",
            "source_url",
            "content",
            "content_type",
            "item_metadata",
            "created_at",
            "owner_id",
        }
        assert columns["id"]["nullable"] is False
        assert columns["owner_id"]["nullable"] is False
        assert columns["title"]["nullable"] is False
        assert columns["description"]["nullable"] is True
        assert columns["created_at"]["nullable"] is True
        assert str(columns["id"]["type"]) == "UUID"
        assert str(columns["owner_id"]["type"]) == "UUID"
        assert str(columns["title"]["type"]) == "VARCHAR(255)"
        assert str(columns["description"]["type"]) == "VARCHAR(255)"
        assert str(columns["source_url"]["type"]) == "VARCHAR(2048)"
        assert str(columns["content"]["type"]) == "TEXT"
        assert str(columns["content_type"]["type"]) == "VARCHAR(50)"
        assert str(columns["item_metadata"]["type"]) == "JSON"
        assert str(columns["created_at"]["type"]) == "TIMESTAMP"
        assert columns["created_at"]["type"].timezone is True

        index_names = {index["name"] for index in inspector.get_indexes("item")}
        assert "ix_item_owner_id" in index_names

        owner_fk = next(
            fk
            for fk in inspector.get_foreign_keys("item")
            if fk["name"] == "item_owner_id_fkey"
        )
        assert owner_fk["constrained_columns"] == ["owner_id"]
        assert owner_fk["referred_table"] == "user"
        assert owner_fk.get("options", {}).get("ondelete") == "CASCADE"
    finally:
        engine.dispose()


def _assert_item_row_count(database_url: str, *, expected_count: int) -> None:
    """Inspect donor rows only while the schema exists."""

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            actual_count = connection.execute(
                text('SELECT count(*) FROM "item"')
            ).scalar_one()
        assert actual_count == expected_count
    finally:
        engine.dispose()


def _assert_downgraded_item_schema(database_url: str) -> None:
    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        columns = {column["name"]: column for column in inspector.get_columns("item")}
        assert columns["owner_id"]["nullable"] is False
        assert {
            "source_url",
            "content",
            "content_type",
            "item_metadata",
        }.isdisjoint(columns)

        index_names = {index["name"] for index in inspector.get_indexes("item")}
        assert "ix_item_owner_id" not in index_names

        owner_fk = next(
            fk
            for fk in inspector.get_foreign_keys("item")
            if fk["name"] == "item_owner_id_fkey"
        )
        assert owner_fk["constrained_columns"] == ["owner_id"]
        assert owner_fk["referred_table"] == "user"
        assert owner_fk.get("options", {}).get("ondelete") is None
    finally:
        engine.dispose()


def _load_migration(filename: str) -> ModuleType:
    migration_path = MIGRATIONS_DIR / filename
    spec = importlib.util.spec_from_file_location(
        f"migration_{migration_path.stem}",
        migration_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_uuid_id_migration_downgrade_is_explicitly_blocked() -> None:
    migration = _load_migration(
        "d98dd8ec85a3_edit_replace_id_integers_in_all_models_.py"
    )
    with pytest.raises(CommandError, match="Downgrade blocked"):
        migration.downgrade()


def test_cascade_delete_migration_uses_named_fk_and_non_nullable_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    migration = _load_migration("1a31ce608336_add_cascade_delete_relationships.py")
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
    fake_op = SimpleNamespace(
        alter_column=lambda *args, **kwargs: calls.append(
            ("alter_column", args, kwargs)
        ),
        drop_constraint=lambda *args, **kwargs: calls.append(
            ("drop_constraint", args, kwargs)
        ),
        create_foreign_key=lambda *args, **kwargs: calls.append(
            ("create_foreign_key", args, kwargs)
        ),
    )
    monkeypatch.setattr(migration, "op", fake_op)

    migration.upgrade()
    migration.downgrade()

    drop_calls = [call for call in calls if call[0] == "drop_constraint"]
    create_fk_calls = [call for call in calls if call[0] == "create_foreign_key"]
    alter_calls = [call for call in calls if call[0] == "alter_column"]

    assert len(drop_calls) == 2
    assert all(call[1][0] == "item_owner_id_fkey" for call in drop_calls)

    assert len(create_fk_calls) == 2
    assert create_fk_calls[0][1][0] == "item_owner_id_fkey"
    assert create_fk_calls[0][2]["ondelete"] == "CASCADE"
    assert create_fk_calls[1][1][0] == "item_owner_id_fkey"
    assert "ondelete" not in create_fk_calls[1][2]

    assert len(alter_calls) == 2
    assert all(call[2]["nullable"] is False for call in alter_calls)


def test_item_owner_index_migration_adds_and_removes_index(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    migration = _load_migration("6f1d0f1e9b9b_add_item_owner_id_index.py")
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
    fake_op = SimpleNamespace(
        f=lambda value: value,
        create_index=lambda *args, **kwargs: calls.append(
            ("create_index", args, kwargs)
        ),
        drop_index=lambda *args, **kwargs: calls.append(("drop_index", args, kwargs)),
    )
    monkeypatch.setattr(migration, "op", fake_op)

    migration.upgrade()
    migration.downgrade()

    assert calls[0][0] == "create_index"
    assert calls[0][1] == ("ix_item_owner_id", "item", ["owner_id"])
    assert calls[0][2] == {"unique": False}

    assert calls[1][0] == "drop_index"
    assert calls[1][1] == ("ix_item_owner_id",)
    assert calls[1][2] == {"table_name": "item"}


def test_donor_retirement_migration_drops_and_recreates_complete_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The destructive revision is reversible only at the schema level."""

    migration = _load_migration("a7d9c2e4f601_drop_donor_item_table.py")
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
    fake_op = SimpleNamespace(
        f=lambda value: value,
        drop_table=lambda *args, **kwargs: calls.append(("drop_table", args, kwargs)),
        create_table=lambda *args, **kwargs: calls.append(
            ("create_table", args, kwargs)
        ),
        create_index=lambda *args, **kwargs: calls.append(
            ("create_index", args, kwargs)
        ),
    )
    monkeypatch.setattr(migration, "op", fake_op)

    migration.upgrade()
    migration.downgrade()

    assert calls[0] == ("drop_table", ("item",), {})
    create_table_call = calls[1]
    assert create_table_call[0] == "create_table"
    assert create_table_call[1][0] == "item"
    donor_columns = {
        argument.name
        for argument in create_table_call[1][1:]
        if hasattr(argument, "name") and argument.name is not None
    }
    assert donor_columns == {
        "id",
        "title",
        "description",
        "source_url",
        "content",
        "content_type",
        "item_metadata",
        "created_at",
        "owner_id",
        "item_pkey",
        "item_owner_id_fkey",
    }
    assert calls[2] == (
        "create_index",
        ("ix_item_owner_id", "item", ["owner_id"]),
        {"unique": False},
    )


def test_clean_database_upgrades_to_item_free_head() -> None:
    """A fresh database reaches the same item-free schema as an existing one."""

    alembic_config = _get_alembic_config()
    with _temporary_database() as db_name, _use_database(db_name):
        command.upgrade(alembic_config, "head")
        _assert_item_table_is_absent(str(settings.SQLALCHEMY_DATABASE_URI))


def test_populated_existing_database_upgrade_drops_donor_rows() -> None:
    """Upgrade intentionally removes the complete donor table and its data."""

    alembic_config = _get_alembic_config()
    with _temporary_database() as db_name, _use_database(db_name):
        command.upgrade(alembic_config, "fe56fa70289e")
        database_url = str(settings.SQLALCHEMY_DATABASE_URI)
        engine = create_engine(database_url)
        owner_id = uuid4()
        donor_item_id = uuid4()
        try:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        'INSERT INTO "user" '
                        "(email, is_active, is_superuser, full_name, id, "
                        "hashed_password, created_at) "
                        "VALUES (:email, true, false, null, :id, :password, now())"
                    ),
                    {
                        "email": "migration-owner@example.com",
                        "id": owner_id,
                        "password": "not-a-real-password-hash",
                    },
                )
                connection.execute(
                    text(
                        'INSERT INTO "item" '
                        "(id, title, description, owner_id, source_url, content, "
                        "content_type, item_metadata, created_at) "
                        "VALUES (:id, :title, null, :owner_id, null, null, "
                        "null, null, now())"
                    ),
                    {
                        "id": donor_item_id,
                        "title": "Donor row intentionally retired",
                        "owner_id": owner_id,
                    },
                )
        finally:
            engine.dispose()
        _assert_item_row_count(database_url, expected_count=1)

        command.upgrade(alembic_config, "head")

        _assert_item_table_is_absent(database_url)


def test_head_downgrade_recreates_empty_schema_then_reupgrade_removes_it() -> None:
    """Rollback restores compatibility, never intentionally deleted rows."""

    alembic_config = _get_alembic_config()
    with _temporary_database() as db_name, _use_database(db_name):
        command.upgrade(alembic_config, "head")
        database_url = str(settings.SQLALCHEMY_DATABASE_URI)
        _assert_item_table_is_absent(database_url)

        command.downgrade(alembic_config, "fe56fa70289e")
        _assert_pre_retirement_item_schema(database_url)
        _assert_item_row_count(database_url, expected_count=0)

        command.upgrade(alembic_config, "head")
        _assert_item_table_is_absent(database_url)


def test_pre_retirement_round_trip_to_d98_preserves_historical_invariants() -> None:
    """Historical migration coverage remains independent of the new head."""

    alembic_config = _get_alembic_config()
    with _temporary_database() as db_name, _use_database(db_name):
        command.upgrade(alembic_config, "fe56fa70289e")
        database_url = str(settings.SQLALCHEMY_DATABASE_URI)
        _assert_pre_retirement_item_schema(database_url)

        command.downgrade(alembic_config, "d98dd8ec85a3")
        _assert_downgraded_item_schema(database_url)

        command.upgrade(alembic_config, "fe56fa70289e")
        _assert_pre_retirement_item_schema(database_url)
