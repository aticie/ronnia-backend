import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import BulkWriteError

from app.models.db import DBUser, DBSetting

logger = logging.getLogger(__name__)


class AsyncMongoClient(AsyncIOMotorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users_db = self.get_database("Ronnia")
        self.statistics_db = self.get_database("Ronnia-Statistics")
        self.users_collection = self.users_db.get_collection("Users")
        self.user_settings_collection = self.users_db.get_collection("UserSettings")
        self.settings_collection = self.users_db.get_collection("Settings")
        self.exclude_collection = self.users_db.get_collection("ExcludeList")

    async def get_user_from_twitch_id(self, twitch_id: int) -> DBUser:
        logger.info(f"Getting user from twitch id: {twitch_id}")
        user = await self.users_collection.find_one({"twitchId": twitch_id})
        if user is not None:
            logger.info(f"Found user: {user}")
            return DBUser(**user)
        logger.info(f"User not found")

    async def get_user_from_osu_id(self, osu_id: int) -> DBUser:
        logger.info(f"Getting user from osu id: {osu_id}")
        user = await self.users_collection.find_one({"osuId": osu_id})
        if user is not None:
            logger.info(f"Found user: {user}")
            return DBUser(**user)
        logger.info(f"User not found")

    async def upsert_user(self, user: dict):
        logger.info(f"Upserting user: {user}")
        return await self.users_collection.update_one(
            {"osuId": user["osuId"]}, {"$set": user}, upsert=True
        )

    async def remove_user_by_twitch_id(self, twitch_id: int):
        logger.info(f"Removing user by twitch id: {twitch_id}")
        return await self.users_collection.delete_one({"twitchId": twitch_id})

    async def bulk_write_operations(self, operations: list, collection: str = "Users"):
        logger.info(f"Bulk writing {len(operations)} operations..")
        col = self.users_db.get_collection(collection)
        try:
            result = await col.bulk_write(operations)
            return result
        except BulkWriteError as bwe:
            logger.error(bwe.details)

    async def get_default_settings(self):
        logger.info("Getting default settings...")
        settings = await self.settings_collection.find().to_list(length=100)
        logger.info(f"Found {len(settings)} settings.")
        return [DBSetting(**setting) for setting in settings]
