from typing import Annotated

from fastapi import APIRouter, Query, Path, HTTPException, status, Depends

from core.rbac import get_current_active_user, require_permission
from models.widget import create_widget, get_widget, get_widgets, update_widget, delete_widget, count_widgets
from schemas.user import User, Permission
from schemas.widget import WidgetCreate, Widget, WidgetUpdate

router = APIRouter(
    prefix="/widgets",
    tags=["widgets"],
)


@router.post(
    "/",
    response_model=Widget,
    dependencies=[Depends(require_permission(Permission.CREATE_WIDGET))],
)
async def create_new_widget(
        widget: WidgetCreate,
        current_user: User = Depends(get_current_active_user)
) -> Widget:
    """Create a new widget."""
    return await create_widget(widget, str(current_user.id))


@router.get(
    "/",
    response_model=list[Widget],
    summary="List all widgets for a given user.",
    description="Retrieve paginated list of widgets for a given user. Optional filtering by category.",
    dependencies=[Depends(require_permission(Permission.READ_WIDGET))],
    responses={
        status.HTTP_200_OK: {
            "description": "List of widgets",
            "model": list[Widget]
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized. Authentication credentials were not provided.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Not authenticated"
                    }
                }
            }
        }
    }
)
async def read_widgets(
        skip: Annotated[int, Query(ge=0, description="Number of rows to skip")] = 0,
        limit: Annotated[int, Query(ge=1, le=100, description="Numbers of records to retrieve")] = 10,
        category: Annotated[str | None, Query(description="Category name")] = None,
        current_user: User = Depends(get_current_active_user)
):
    """Retrieve widgets with optional filtering."""
    return await get_widgets(str(current_user.id), skip, limit, category)


@router.get(
    "/count"
)
async def count_user_widgets(
        current_user: str = "abc",
        category: str | None = None
):
    """Count user`s widgets with optional filtering"""
    count = await count_widgets(current_user, category)
    return {"count": count}


@router.get(
    "/{widget_id}",
    response_model=Widget
)
async def read_widget(
        widget_id: str = Path(..., title="The ID of the widget to get."),
        current_user: str = "abc"
):
    """ Get a specific widget by id. """
    widget = await get_widget(widget_id, current_user)
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found"
        )

    return widget


@router.patch(
    "/{widget_id}",
    response_model=Widget
)
async def update_existing_widget(
        widget_update: WidgetUpdate,
        widget_id: str = Path(..., title="The ID of the widget to update."),
        current_user: str = "abc"
):
    """ Update a widget"""
    updated_widget = await update_widget(widget_id, current_user, widget_update)
    if not updated_widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found"
        )

    return updated_widget


@router.delete(
    "/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_widget(
        widget_id: str = Path(..., title="The ID of the widget to delete."),
        current_user: str = "abc"
):
    """Delete a widget"""
    deleted = await delete_widget(widget_id, current_user)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found"
        )
    return None
