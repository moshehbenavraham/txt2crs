"""
EXAMPLE: Paginated user list query with filtering.

PATTERN: Paginated List with Count
USE WHEN: Implementing administrator list endpoints
TAGS: crud, pagination, filtering, list

This example demonstrates:
1. Skip/limit pagination
2. A count derived from the same filtered query as the returned page
3. Optional active-state filtering
4. Conversion from table models to public response models

Based on: app/api/routes/users.py:read_users
"""

from sqlmodel import Session, col, func, select

from app.models import User, UserPublic, UsersPublic


def get_users_paginated(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> UsersPublic:
    """Return one filtered user page plus its exact total count."""

    user_query = select(User)
    if is_active is not None:
        user_query = user_query.where(User.is_active == is_active)

    # Count the complete filtered relation before applying page bounds.
    count_query = select(func.count()).select_from(user_query.subquery())
    total_count = session.exec(count_query).one()

    page_query = (
        user_query.order_by(col(User.created_at).desc().nulls_last())
        .offset(skip)
        .limit(limit)
    )
    users = session.exec(page_query).all()
    return UsersPublic(
        data=[UserPublic.model_validate(user) for user in users],
        count=total_count,
    )


# Route usage:
#
# @router.get("/users", response_model=UsersPublic)
# def read_users_example(
#     session: SessionDep,
#     skip: Annotated[int, Query(ge=0)] = 0,
#     limit: Annotated[int, Query(ge=1, le=100)] = 100,
#     is_active: bool | None = None,
# ) -> UsersPublic:
#     return get_users_paginated(
#         session=session,
#         skip=skip,
#         limit=limit,
#         is_active=is_active,
#     )
#
# The route must still enforce administrator authorization through its
# dependency. Filtering a query is not an authorization boundary.
