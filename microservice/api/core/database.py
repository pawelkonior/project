from pymongo import AsyncMongoClient

from core.config import settings

client = AsyncMongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

users_collection = db.users
widgets_collection = db.widgets