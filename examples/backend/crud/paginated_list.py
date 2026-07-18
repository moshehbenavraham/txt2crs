"""
EXAMPLE: Paginated list query with filtering

PATTERN: Paginated List with Count
USE WHEN: Implementing list endpoints that return paginated results
TAGS: crud, pagination, filtering, list

This example demonstrates:
1. Skip/limit pagination pattern
2. Total count query (separate from data query)
3. Optional filtering by field value
4. Owner-scoped queries (user can only see their own items)

Based on: app/api/routes/items.py:read_items
"""

import uuid
from typing import Literal

from sqlmodel import Session, func, select

from app.models import Item, ItemsPublic

# Type alias for content type filter options
ContentTypeFilter = Literal["general"] | None


def get_items_paginated(
    *,
    session: Session,
    owner_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    content_type: ContentTypeFilter = None,
) -> ItemsPublic:
    """
    Retrieve a paginated list of items with optional filtering.

    Preconditions:
        - session is an active database session
        - skip >= 0
        - 1 <= limit <= 100

    Postconditions:
        - Returns ItemsPublic with data list and total count
        - Count reflects total matching items (ignoring pagination)
        - Data reflects items within skip/limit window

    Args:
        session: Database session for query execution.
        owner_id: If provided, filter to items owned by this user.
                  If None, returns all items (superuser behavior).
        skip: Number of items to skip for pagination. Defaults to 0.
        limit: Maximum number of items to return. Defaults to 100.
        content_type: Optional filter by content type.

    Returns:
        ItemsPublic containing list of items and total count.

    Example:
        >>> # Get first page of user's items
        >>> result = get_items_paginated(
        ...     session=session,
        ...     owner_id=current_user.id,
        ...     skip=0,
        ...     limit=20
        ... )
        >>> print(f"Showing {len(result.data)} of {result.count} items")

        >>> # Get second page with filter
        >>> result = get_items_paginated(
        ...     session=session,
        ...     owner_id=current_user.id,
        ...     skip=20,
        ...     limit=20,
        ...     content_type="general"
        ... )
    """
    # Step 1: Build base queries (count and data)
    # IMPORTANT: Two separate queries for count vs data
    base_count = select(func.count()).select_from(Item)
    base_query = select(Item)

    # Step 2: Apply owner filter if provided
    if owner_id is not None:
        base_count = base_count.where(Item.owner_id == owner_id)
        base_query = base_query.where(Item.owner_id == owner_id)

    # Step 3: Apply content_type filter if provided
    if content_type is not None:
        base_count = base_count.where(Item.content_type == content_type)
        base_query = base_query.where(Item.content_type == content_type)

    # Step 4: Execute count query (total matching, ignores pagination)
    count = session.exec(base_count).one()

    # Step 5: Execute data query with pagination
    items = session.exec(base_query.offset(skip).limit(limit)).all()

    # Step 6: Return structured response
    return ItemsPublic(data=items, count=count)


# === USAGE IN ROUTE HANDLER ===
#
# @router.get("/", response_model=ItemsPublic)
# def read_items(
#     session: SessionDep,
#     current_user: CurrentUser,
#     skip: Annotated[int, Query(ge=0)] = 0,
#     limit: Annotated[int, Query(ge=1, le=100)] = 100,
#     content_type: ContentTypeFilter = None,
# ) -> ItemsPublic:
#     # Superusers see all, regular users see only their own
#     owner_id = None if current_user.is_superuser else current_user.id
#     return get_items_paginated(
#         session=session,
#         owner_id=owner_id,
#         skip=skip,
#         limit=limit,
#         content_type=content_type,
#     )


# === KEY PATTERNS USED ===
#
# 1. Separate count and data queries
#    - Count uses func.count() for efficiency
#    - Data query uses actual select
#
# 2. Progressive filter application
#    - Start with base query
#    - Add filters conditionally
#    - Apply pagination last
#
# 3. Response model with count
#    - Always include total count for pagination UI
#    - ItemsPublic(data=..., count=...)
#
# 4. Literal type for filter options
#    - ContentTypeFilter = Literal["general"] | None
#    - Enables autocomplete and validation
