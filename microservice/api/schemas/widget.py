from datetime import datetime
from decimal import Decimal
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, PositiveInt, model_validator, Field, ConfigDict, field_serializer

from utils.sanitizer import sanitize_string


class WidgetBase(BaseModel):
    """Base widget schema"""

    name: str
    description: str | None = None
    price: float
    quantity: PositiveInt
    category: str

    @model_validator(mode='before')
    @classmethod
    def model_validate(cls, data: Any) -> Any:
        for field in ["name", "description", "category"]:
            if field in data and data[field]:
                data[field] = sanitize_string(data[field])
        return data


class WidgetCreate(WidgetBase):
    """Schema for creating a widget"""
    pass


class WidgetUpdate(WidgetBase):
    """Schema for updating a widget"""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: PositiveInt | None = None
    category: str | None = None


class Widget(WidgetBase):
    """Schema for a widget"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: ObjectId = Field(alias="_id")
    owner: str
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer("id")
    def serialize_id(self, value: ObjectId) -> str:
        return str(value)
