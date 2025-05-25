from typing import Annotated

from fastapi import APIRouter, Query, HTTPException, status, Depends, Path

from core.rbac import require_permission, get_current_active_user, has_permission
from schemas.user import User, UserCreate, Permission, UserUpdate, Role
from models.user import get_user_by_username, get_user_by_email, create_user, get_all_users, get_user_by_id, \
    update_user, add_user_permission, update_user_role

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/",
    response_model=User
)
async def register_user(user: UserCreate):
    """Register a new user."""
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    existing_email = await get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists."
        )

    return await create_user(user)


@router.get(
    "/",
    response_model=list[User],
    dependencies=[Depends(require_permission(Permission.READ_USER))]
)
async def read_users(
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """Get all users (requires READ_USER permission)"""
    return await get_all_users(skip, limit)


@router.get(
    "/me",
    response_model=User,
)
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get(
    "/{user_id}",
    response_model=User,
    dependencies=[Depends(require_permission(Permission.READ_USER))]
)
async def read_user(user_id: str = Path(..., title="The ID of the user to get.")):
    """Get a specific user by id (requires READ_USER permission)"""
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.patch("/{user_id}", response_model=User)
async def update_user_details(
        user_update: UserUpdate,
        user_id: str = Path(..., title="The ID of the user to update."),
        current_user: User = Depends(get_current_active_user)
):
    if str(current_user.id) != user_id and not has_permission(current_user, Permission.UPDATE_USER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )

    try:
        updated_user = await update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch(
    "/{user_id}/role",
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def update_role(
        role: Role,
        user_id: str = Path(..., title="The ID of the user to update."),
):
    user = await update_user_role(user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch(
    "/{user_id}/status",
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def update_user_status(
        disabled: bool,
        user_id: str = Path(..., title="The ID of the user to update."),
):
    updated = await update_user_status(disabled, user_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user = await get_user_by_id(user_id)
    return user


@router.post(
    "/{user_id}/permissions",
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def add_permission(
        permission: Permission,
        user_id: str = Path(..., title="The ID of the user to update."),
):
    user = await add_user_permission(user_id, permission)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
