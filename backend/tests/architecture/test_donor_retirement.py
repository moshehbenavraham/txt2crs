"""Static boundary checks for complete backend donor-domain retirement."""

from pathlib import Path

from app import models
from app.main import app

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_donor_modules_tests_and_feature_document_are_removed() -> None:
    """No executable or test-only donor module remains after replacement."""

    removed_paths = (
        "backend/app/api/routes/items.py",
        "backend/tests/api/routes/test_items.py",
        "backend/tests/models/test_item_models.py",
        "backend/tests/utils/item.py",
        "docs/items-feature.md",
    )
    for relative_path in removed_paths:
        assert not (REPOSITORY_ROOT / relative_path).exists(), relative_path


def test_current_models_routes_crud_and_errors_have_no_donor_contract() -> None:
    """The current application exposes jobs and users without Item symbols."""

    for retired_model_name in (
        "ContentType",
        "ItemBase",
        "ItemCreate",
        "ItemUpdate",
        "Item",
        "ItemPublic",
        "ItemsPublic",
    ):
        assert not hasattr(models, retired_model_name), retired_model_name

    route_paths = {
        route.path
        for route in app.routes
        if isinstance(getattr(route, "path", None), str)
    }
    assert not any(path.startswith("/api/v1/items") for path in route_paths)

    source_checks = {
        "backend/app/api/main.py": ("items,", "items.router"),
        "backend/app/api/deps.py": ("select(Item)",),
        "backend/app/api/routes/users.py": (
            "delete(Item)",
            "from app.models import Item",
        ),
        "backend/app/crud.py": (
            "def create_item",
            "ItemCreate",
            "from app.models import Item",
        ),
        "backend/app/core/constants.py": (
            "ITEM_",
            "ItemContentTypes",
            "get_items(",
        ),
        "backend/app/core/exceptions.py": ('"Item":', "ErrorCode.ITEM_"),
        "backend/app/core/exception_handlers.py": ("item not found", "ITEM_NOT_FOUND"),
    }
    for relative_path, retired_fragments in source_checks.items():
        source = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        for retired_fragment in retired_fragments:
            assert retired_fragment not in source, (
                f"{retired_fragment!r} remains in {relative_path}"
            )


def test_current_documentation_makes_no_donor_api_or_schema_claim() -> None:
    """Operational docs describe the replacement instead of the donor domain."""

    documentation_checks = {
        "backend/README_backend.md": (
            "Temporary donor domain",
            "/api/v1/items",
        ),
        "backend/tests/README_backend_tests.md": ("users, items",),
        "docs/ARCHITECTURE.md": ("temporary donor items", "temporary items"),
        "docs/adr/0004-rfc9457-error-format.md": (
            "| 3xxx | Item |",
            "ITEM_3001",
        ),
        "docs/api/README_api.md": ("/api/v1/items",),
        "docs/dashboard-design.md": ("ItemsPublic", "Total item count"),
        "docs/database/SCHEMA.md": (
            "### Item Table",
            "User -> Item",
            "select(Item)",
        ),
    }
    for relative_path, retired_claims in documentation_checks.items():
        document = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        for retired_claim in retired_claims:
            assert retired_claim not in document, (
                f"{retired_claim!r} remains in {relative_path}"
            )


def test_current_documentation_names_real_public_erasure_and_job_contracts() -> None:
    """Examples must use the facade method and response type that actually exist."""

    database_document = (REPOSITORY_ROOT / "docs/database/SCHEMA.md").read_text(
        encoding="utf-8"
    )
    assert "Txt2CrsApplication.purge_owner(user_id=target_user_id)" in (
        database_document
    )
    assert "purge_owner_data" not in database_document

    dashboard_document = (REPOSITORY_ROOT / "docs/dashboard-design.md").read_text(
        encoding="utf-8"
    )
    assert "`JobStatusPublic`" in dashboard_document
    assert "`JobPublic`" not in dashboard_document


def test_backend_agent_guidance_and_examples_use_current_shell_contracts() -> None:
    """Few-shot guidance cannot import models or errors removed from the shell."""

    guidance_checks = {
        "backend/AGENTS.md": (
            '"/items',
            "ItemPublic",
            "ItemsPublic",
            "ErrorCode.ITEM_",
        ),
        "examples/backend/crud/update_partial.py": (
            "from app.models import Item",
            "ItemUpdate",
            "ErrorCode.ITEM_",
        ),
        "examples/backend/crud/paginated_list.py": (
            "from app.models import Item",
            "ItemsPublic",
        ),
        "examples/backend/api/authenticated_endpoint.py": (
            "from app.models import Item",
            '"/items',
            "ItemPublic",
        ),
        "examples/backend/api/error_handling.py": (
            "from app.models import Item",
            "ErrorCode.ITEM_",
            "ITEM_300",
        ),
        "examples/backend/testing/unit_test_crud.py": (
            "ItemCreate",
            "ItemUpdate",
        ),
    }
    for relative_path, retired_fragments in guidance_checks.items():
        source = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        for retired_fragment in retired_fragments:
            assert retired_fragment not in source, (
                f"{retired_fragment!r} remains in {relative_path}"
            )
