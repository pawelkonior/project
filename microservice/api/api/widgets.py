from typing import Annotated

from fastapi import APIRouter, Query, Path, HTTPException, status

from models.widget import create_widget, get_widget, get_widgets, update_widget, delete_widget, count_widgets
from schemas.widget import WidgetCreate, Widget, WidgetUpdate

router = APIRouter(
    prefix="/widgets",
    tags=["widgets"],
)


@router.post(
    "/",
    response_model=Widget
)
async def create_new_widget(widget: WidgetCreate) -> Widget:
    """Create a new widget."""
    return await create_widget(widget)


@router.get(
    "/",
    response_model=list[Widget]
)
async def read_widgets(
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 10,
        category: str | None = None,
        current_user: str = "abc"
):
    """Retrieve widgets with optional filtering."""
    return await get_widgets(current_user, skip, limit, category)


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
