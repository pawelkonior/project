from typing import Any
from enum import Enum

from pydantic import BaseModel, EmailStr, model_validator, Field, ConfigDict, field_serializer
from bson import ObjectId

from utils.sanitizer import sanitize_string


class Role(str, Enum):
    """User roles for RBAC"""
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'


class Permission(str, Enum):
    """Permissions for RBAC"""

    # Widget permissions
    CREATE_WIDGET = "create:widget"
    READ_WIDGET = "read:widget"
    UPDATE_WIDGET = "update:widget"
    DELETE_WIDGET = "delete:widget"

    # User permission
    CREATE_USER = "create:user"
    READ_USER = "read:user"
    UPDATE_USER = "update:user"
    DELETE_USER = "delete:user"

    # Admin permissions
    MANAGE_ROLES = "manage:roles"
    VIEW_METRICS = "view:metrics"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str

    @model_validator(mode='before')
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if data.get('username'):
            data['username'] = sanitize_string(data['username'])
        return data


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    role: Role = Role.USER


class UserUpdate(UserBase):
    """Schema for updating a user"""
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class User(UserBase):
    """Schema for a user"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    role: Role = Role.USER
    permissions: list[Permission] = []
    disabled: bool = False

    @field_serializer("id")
    def serialize_id(self, value: ObjectId) -> str:
        return str(value)
