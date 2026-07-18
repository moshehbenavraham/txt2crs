"""
EXAMPLE: Authenticated API endpoint with OpenAPI documentation

PATTERN: REST Endpoint with Auth, Validation, and Rich OpenAPI
USE WHEN: Creating new API endpoints that require authentication
TAGS: api, auth, openapi, validation, endpoint

This example demonstrates:
1. JWT authentication via dependency injection
2. Rich OpenAPI documentation (summary, description, responses)
3. Path and query parameter validation with Annotated
4. Proper response model usage
5. Error response documentation

Based on: app/api/routes/items.py
"""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Path

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic

router = APIRouter(prefix="/example", tags=["example"])


@router.post(
    "/items/",
    response_model=ItemPublic,
    status_code=201,
    summary="Create a new item",
    description="""
Create a new item owned by the authenticated user.

**Request Body:**
- `title` (required): Item title, 1-255 characters
- `description` (optional): Short description, max 255 characters
- `content_type` (optional): Defaults to "general"

**Authentication:** Bearer token required.

**Rate Limit:** 100 requests per minute.
    """,
    responses={
        201: {
            "description": "Item successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Meeting Notes",
                        "description": "Q4 planning meeting notes",
                        "content_type": "general",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        401: {"description": "Not authenticated - missing or invalid token"},
        422: {"description": "Validation error - check request body format"},
    },
)
def create_item_example(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_in: ItemCreate,
) -> Any:
    """
    Create a new item for the current user.

    The item is automatically assigned to the authenticated user.
    """
    # Step 1: Create item with owner_id from authenticated user
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})

    # Step 2: Persist to database
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@router.get(
    "/items/{item_id}",
    response_model=ItemPublic,
    summary="Get item by ID",
    description="""
Retrieve a single item by its unique identifier.

**Access Control:**
- Regular users can only retrieve items they own
- Superusers can retrieve any item

**Path Parameters:**
- `item_id`: UUID of the item to retrieve
    """,
    responses={
        200: {
            "description": "Item successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Meeting Notes",
                        "description": "Q4 planning meeting notes",
                        "content_type": "general",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        400: {"description": "Insufficient permissions to access this item"},
        401: {"description": "Not authenticated"},
        404: {"description": "Item not found"},
    },
)
def read_item_example(
    session: SessionDep,
    current_user: CurrentUser,
    item_id: Annotated[
        uuid.UUID,
        Path(
            description="Unique identifier of the item",
            example="550e8400-e29b-41d4-a716-446655440000",
        ),
    ],
) -> Any:
    """
    Get a single item by ID with ownership validation.
    """
    # Step 1: Retrieve item from database
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Step 2: Check ownership (unless superuser)
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return item


# === KEY PATTERNS USED ===
#
# 1. Dependency Injection for Auth
#    - SessionDep: Injects database session
#    - CurrentUser: Injects authenticated user (or raises 401)
#
# 2. Rich OpenAPI Decorators
#    - summary: Short description in API docs
#    - description: Detailed markdown documentation
#    - responses: Document all possible response codes
#
# 3. Annotated Type Hints for Parameters
#    - Annotated[uuid.UUID, Path(...)] for path params
#    - Annotated[int, Query(ge=0, le=100)] for query params
#    - Includes validation and OpenAPI examples
#
# 4. Response Models
#    - response_model=ItemPublic filters output fields
#    - Prevents leaking internal fields (like timestamps)
#
# 5. Status Codes
#    - status_code=201 for resource creation
#    - HTTPException for error responses


# === ANNOTATED PARAMETER EXAMPLES ===
#
# Path parameter with validation:
# item_id: Annotated[
#     uuid.UUID,
#     Path(
#         description="Unique identifier of the item",
#         example="550e8400-e29b-41d4-a716-446655440000",
#     ),
# ]
#
# Query parameter with bounds:
# limit: Annotated[
#     int,
#     Query(
#         ge=1,
#         le=100,
#         description="Maximum items to return",
#         example=20,
#     ),
# ] = 100  # Default value
#
# Optional query parameter:
# search: Annotated[
#     str | None,
#     Query(
#         max_length=100,
#         description="Search term",
#     ),
# ] = None
