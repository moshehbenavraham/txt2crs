"""
EXAMPLE: Partial update with permission check

PATTERN: CRUD Update with Ownership Validation
USE WHEN: Updating existing records where user must own the resource
TAGS: crud, update, validation, permissions, partial-update

This example demonstrates:
1. Partial update (only update provided fields)
2. Ownership validation before modification
3. Using model_dump(exclude_unset=True) for partial updates
4. Proper error handling with semantic error codes

Based on: app/api/routes/items.py:update_item
"""

import uuid

from sqlmodel import Session

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.models import Item, ItemUpdate


def update_item_with_permission_check(
    *,
    session: Session,
    item_id: uuid.UUID,
    item_update: ItemUpdate,
    current_user_id: uuid.UUID,
    is_superuser: bool = False,
) -> Item:
    """
    Update an item with ownership validation.

    Preconditions:
        - session is an active database session
        - item_id references an existing item
        - current_user_id is the authenticated user's ID

    Postconditions:
        - Item fields from item_update are applied
        - Unset fields in item_update remain unchanged
        - Returns updated Item with refreshed data

    Args:
        session: Database session for query execution.
        item_id: UUID of the item to update.
        item_update: Update data (only set fields are applied).
        current_user_id: ID of the user making the request.
        is_superuser: If True, skip ownership check.

    Returns:
        The updated Item object.

    Raises:
        AppException: ITEM_NOT_FOUND if item doesn't exist.
        AppException: AUTH_INSUFFICIENT_PERMISSIONS if user doesn't own item.

    Example:
        >>> from app.models import ItemUpdate
        >>> update_data = ItemUpdate(title="New Title", description="Updated desc")
        >>> updated_item = update_item_with_permission_check(
        ...     session=session,
        ...     item_id=item.id,
        ...     item_update=update_data,
        ...     current_user_id=current_user.id,
        ... )
        >>> print(updated_item.title)  # "New Title"
    """
    # Step 1: Retrieve existing item
    item = session.get(Item, item_id)
    if not item:
        raise AppException(
            code=ErrorCode.ITEM_NOT_FOUND,
            detail=f"Item with ID '{item_id}' not found",
        )

    # Step 2: Check ownership (unless superuser)
    if not is_superuser and item.owner_id != current_user_id:
        raise AppException(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail="Not authorized to update this item",
        )

    # Step 3: Apply partial update
    # IMPORTANT: exclude_unset=True means only explicitly set fields are updated
    # This enables PATCH-like behavior where omitted fields stay unchanged
    update_dict = item_update.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)

    # Step 4: Persist changes
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


# === USAGE IN ROUTE HANDLER ===
#
# @router.put("/{id}", response_model=ItemPublic)
# def update_item(
#     session: SessionDep,
#     current_user: CurrentUser,
#     id: uuid.UUID,
#     item_in: ItemUpdate,
# ) -> Item:
#     return update_item_with_permission_check(
#         session=session,
#         item_id=id,
#         item_update=item_in,
#         current_user_id=current_user.id,
#         is_superuser=current_user.is_superuser,
#     )


# === KEY PATTERNS USED ===
#
# 1. model_dump(exclude_unset=True)
#    - Only includes fields that were explicitly set
#    - Enables partial updates (PATCH semantics)
#    - {"title": "New"} only updates title, not description
#
# 2. sqlmodel_update(update_dict)
#    - SQLModel method to apply dict updates to model
#    - More efficient than setting each field manually
#
# 3. Permission check pattern
#    - Check ownership AFTER confirming resource exists
#    - Return NOT_FOUND for non-existent (avoids leaking info)
#    - Superuser bypass for admin operations
#
# 4. Session lifecycle: get -> modify -> add -> commit -> refresh
#    - get() retrieves existing record
#    - add() marks for update (SQLAlchemy tracks changes)
#    - refresh() gets any DB-generated values (updated_at)
