from datetime import datetime, timezone
from bson import ObjectId

from core.database import widgets_collection
from schemas.widget import WidgetCreate, Widget, WidgetUpdate


async def create_widget(widget: WidgetCreate, owner_id: str = "abc") -> Widget:
    """Create a new widget."""
    widget_dict = widget.model_dump()
    widget_dict["owner"] = owner_id
    widget_dict["created_at"] = datetime.now(timezone.utc)

    result = await widgets_collection.insert_one(widget_dict)
    widget_dict["_id"] = result.inserted_id

    # TODO: check validation errors
    return Widget.model_validate(widget_dict)


async def get_widgets(
        owner_id: str,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
) -> list[Widget]:
    """Get widgets by owner with optional filtering"""
    query = {"owner": owner_id}
    if category:
        query["category"] = category

    cursor = widgets_collection.find(query).skip(skip).limit(limit)
    return [Widget.model_validate(widget) async for widget in cursor]


async def get_widget(widget_id: str, owner_id: str) -> Widget | None:
    """Get a widget by id and owner"""
    widget = await widgets_collection.find_one({"_id": ObjectId(widget_id), "owner": owner_id})
    if widget:
        return Widget.model_validate(widget)
    return None


async def update_widget(
        widget_id: str,
        owner_id: str,
        widget: WidgetUpdate
) -> Widget | None:
    """Update a widget by id and owner"""
    update_data = {k: v for k, v in widget.model_dump().items() if v is not None}

    if not update_data:
        return await get_widget(widget_id, owner_id)

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await widgets_collection.update_one(
        {"_id": ObjectId(widget_id), "owner": owner_id},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        return None

    return await get_widget(widget_id, owner_id)


async def delete_widget(widget_id: str, owner_id: str) -> bool:
    """Delete a widget by id and owner"""
    result = await widgets_collection.delete_one({"_id": ObjectId(widget_id), "owner": owner_id})
    return result.deleted_count == 1


async def count_widgets(owner_id: str, category: str | None = None) -> int:
    """Count widgets by owner with optional filtering"""
    query = {"owner": owner_id}
    if category:
        query["category"] = category

    return await widgets_collection.count_documents(query)
