"""
Item management API routes.

This module provides CRUD operations for user items. Items are the core
content unit and can represent notes, documents, or other user-generated content.

All endpoints require authentication. Regular users can only access their
own items; superusers can access all items.
"""

import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Path, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.exceptions import AuthorizationError, NotFoundError
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

ContentTypeFilter = Literal["general"]

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/",
    response_model=ItemsPublic,
    summary="List items",
    description="""
Retrieve a paginated list of items with optional filtering.

**Access Control:**
- Regular users: Returns only items owned by the current user
- Superusers: Returns all items in the system

**Pagination:**
- Use `skip` and `limit` parameters for pagination
- Maximum limit is 100 items per request

**Filtering:**
- Filter by `content_type` to get items of a specific type
    """,
    responses={
        200: {
            "description": "Successfully retrieved items",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "title": "Meeting Notes",
                                "description": "Q4 planning meeting notes",
                                "content_type": "general",
                                "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                            }
                        ],
                        "count": 1,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
    },
)
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="Number of items to skip for pagination",
            examples=[0],
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Maximum number of items to return (1-100)",
            examples=[20],
        ),
    ] = 100,
    content_type: Annotated[
        ContentTypeFilter | None,
        Query(
            description="Filter by content type",
            examples=["general"],
        ),
    ] = None,
) -> Any:
    """Retrieve items with optional content_type filter."""
    if current_user.is_superuser:
        base_count = select(func.count()).select_from(Item)
        base_query = select(Item)
    else:
        base_count = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )
        base_query = select(Item).where(Item.owner_id == current_user.id)

    # Apply content_type filter if provided
    if content_type is not None:
        base_count = base_count.where(Item.content_type == content_type)
        base_query = base_query.where(Item.content_type == content_type)

    count = session.exec(base_count).one()
    items = session.exec(
        base_query.order_by(col(Item.created_at).desc().nulls_last())
        .offset(skip)
        .limit(limit)
    ).all()

    items_public = [ItemPublic.model_validate(item) for item in items]
    return ItemsPublic(data=items_public, count=count)


@router.get(
    "/{id}",
    response_model=ItemPublic,
    summary="Get item by ID",
    description="""
Retrieve a single item by its unique identifier.

**Access Control:**
- Regular users: Can only retrieve items they own
- Superusers: Can retrieve any item
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
        403: {"description": "Not enough permissions to access this item"},
        401: {"description": "Not authenticated"},
        404: {"description": "Item not found"},
    },
)
def read_item(
    session: SessionDep,
    current_user: CurrentUser,
    id: Annotated[
        uuid.UUID,
        Path(
            description="Unique identifier of the item",
            examples=["550e8400-e29b-41d4-a716-446655440000"],
        ),
    ],
) -> Any:
    """Get item by ID."""
    item = session.get(Item, id)
    if not item:
        raise NotFoundError(resource="Item", identifier=str(id))
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise AuthorizationError(detail="Not enough permissions")
    return item


@router.post(
    "/",
    response_model=ItemPublic,
    status_code=201,
    summary="Create item",
    description="""
Create a new item owned by the current user.

The item will be automatically assigned to the authenticated user.
All items have a `content_type` that defaults to "general".
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
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error in request body"},
    },
)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """Create new item."""
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put(
    "/{id}",
    response_model=ItemPublic,
    summary="Update item",
    description="""
Update an existing item by ID.

**Partial Updates:**
Only fields included in the request body will be updated.
Omitted fields retain their current values.

**Access Control:**
- Regular users: Can only update items they own
- Superusers: Can update any item
    """,
    responses={
        200: {
            "description": "Item successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Updated Meeting Notes",
                        "description": "Updated Q4 planning notes",
                        "content_type": "general",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        403: {"description": "Not enough permissions to update this item"},
        401: {"description": "Not authenticated"},
        404: {"description": "Item not found"},
        422: {"description": "Validation error in request body"},
    },
)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: Annotated[
        uuid.UUID,
        Path(
            description="Unique identifier of the item to update",
            examples=["550e8400-e29b-41d4-a716-446655440000"],
        ),
    ],
    item_in: ItemUpdate,
) -> Any:
    """Update an item."""
    item = session.get(Item, id)
    if not item:
        raise NotFoundError(resource="Item", identifier=str(id))
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise AuthorizationError(detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete(
    "/{id}",
    response_model=Message,
    summary="Delete item",
    description="""
Permanently delete an item by ID.

**Warning:** This action cannot be undone.

**Access Control:**
- Regular users: Can only delete items they own
- Superusers: Can delete any item
    """,
    responses={
        200: {
            "description": "Item successfully deleted",
            "content": {
                "application/json": {
                    "example": {"message": "Item deleted successfully"}
                }
            },
        },
        403: {"description": "Not enough permissions to delete this item"},
        401: {"description": "Not authenticated"},
        404: {"description": "Item not found"},
    },
)
def delete_item(
    session: SessionDep,
    current_user: CurrentUser,
    id: Annotated[
        uuid.UUID,
        Path(
            description="Unique identifier of the item to delete",
            examples=["550e8400-e29b-41d4-a716-446655440000"],
        ),
    ],
) -> Message:
    """Delete an item."""
    item = session.get(Item, id)
    if not item:
        raise NotFoundError(resource="Item", identifier=str(id))
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise AuthorizationError(detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
