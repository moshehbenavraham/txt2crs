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


def _assert_head_item_schema(database_url: str) -> None:
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
        }.issubset(columns)

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


def test_alembic_round_trip_head_to_d98_and_back_preserves_item_schema_invariants() -> (
    None
):
    alembic_config = _get_alembic_config()
    with _temporary_database() as db_name, _use_database(db_name):
        command.upgrade(alembic_config, "head")
        database_url = str(settings.SQLALCHEMY_DATABASE_URI)
        _assert_head_item_schema(database_url)

        command.downgrade(alembic_config, "d98dd8ec85a3")
        _assert_downgraded_item_schema(database_url)

        command.upgrade(alembic_config, "head")
        _assert_head_item_schema(database_url)
