from bson import ObjectId

from pydantic import EmailStr

from core.database import users_collection
from core.rbac import get_permissions_for_role
from schemas.user import User, UserCreate, Role, Permission, UserUpdate
from core.security import get_password_hash, verify_password


def get_if_user_exists(user) -> User | None:
    if user:
        return User.model_validate(user)
    return None


async def get_user_by_username(username: str) -> User | None:
    """Get a user by username."""
    user = await users_collection.find_one({"username": username})
    return get_if_user_exists(user)


async def get_user_by_email(email: EmailStr) -> User | None:
    """Get a user by email."""
    user = await users_collection.find_one({"email": email})
    return get_if_user_exists(user)


async def get_user_by_id(user_id: str) -> User | None:
    """Get a user by id."""
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    return get_if_user_exists(user)


async def create_user(user: UserCreate) -> User:
    """Create a new user."""
    user_dict = user.model_dump()
    user_dict["password"] = get_password_hash(user_dict["password"])

    role = user_dict.get("role", Role.USER)
    permissions = get_permissions_for_role(role)
    user_dict["permissions"] = permissions
    user_dict["disabled"] = False

    result = await users_collection.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id

    return User.model_validate(user_dict)


async def get_all_users(skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users (for admin purposes)"""
    cursor = users_collection.find().skip(skip).limit(limit)
    return [User.model_validate(user) async for user in cursor]


async def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a user with a username and password."""
    user_dict = await users_collection.find_one({"username": username})
    if not user_dict:
        return None
    if not verify_password(password, user_dict["password"]):
        return None
    return User.model_validate(user_dict)


async def update_user_status(user_id: str, disabled: bool) -> bool:
    """Update a user`s disabled status"""
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"disabled": disabled}}
    )
    return result.modified_count == 1


async def update_user_role(user_id: str, role: Role) -> User | None:
    """Update a user`s role"""
    permissions = get_permissions_for_role(role)

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": role, "permissions": permissions}}
    )

    if result.modified_count == 1:
        return await get_user_by_id(user_id)
    return None


async def add_user_permission(user_id: str, permission: Permission) -> User | None:
    """Add a permission to a user"""
    user = await get_user_by_id(user_id)
    if not user:
        return None

    current_permissions = user.permissions
    if permission not in current_permissions:
        current_permissions.append(permission)

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"permissions": current_permissions}}
        )

        return await get_user_by_id(user_id)
    return user


async def remove_user_permission(user_id: str, permission: Permission) -> User | None:
    """Remove a permission from a user"""
    user = await get_user_by_id(user_id)
    if not user:
        return None

    current_permissions = user.permissions
    if permission in current_permissions:
        current_permissions.remove(permission)

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"permissions": current_permissions}}
        )

        return await get_user_by_id(user_id)
    return user


async def update_user(user_id: str, user_update: UserUpdate) -> User | None:
    """Update a user"""
    user = await get_user_by_id(user_id)
    if not user:
        return None

    update_data = {}

    if user_update.username is not None and user_update.username != user.username:
        existing_user = await get_user_by_username(user_update.username)
        if existing_user and existing_user.id != user_id:
            raise ValueError("Username already exists")
        update_data["username"] = user_update.username

    if user_update.email is not None and user_update.email != user.email:
        existing_email = await get_user_by_email(user_update.email)
        if existing_email and existing_email.id != user_id:
            raise ValueError("Email already exists.")
        update_data["email"] = user_update.email

    if user_update.password is not None:
        update_data["password"] = get_password_hash(user_update.password)

    if update_data:
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.modified_count == 1 or result.matched_count == 1:
            return await get_user_by_id(user_id)
    else:
        return user

    return None


async def delete_user(user_id: str) -> bool:
    """Delete a user"""
    user = await get_user_by_id(user_id)
    if not user:
        return False

    if user.role == Role.ADMIN:
        admin_count = await users_collection.count_documents({"role": Role.ADMIN})
        if admin_count <= 1:
            return False

    result = await users_collection.delete_one({"_id": ObjectId(user_id)})

    from core.database import widgets_collection
    await widgets_collection.delete_many({"owner": ObjectId(user_id)})

    return result.deleted_count == 1
