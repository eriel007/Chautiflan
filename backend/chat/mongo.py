from pymongo import MongoClient
from django.conf import settings


def get_messages_collection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    return db["messages"]


def get_messages_for_room(room_name, limit=60):
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    collection = db["messages"]
    return list(
        collection.find({"room_name": room_name}).sort("timestamp", -1).limit(limit)
    )
