import logging
from typing import List

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

    async def get_live_users(self, limit: int, offset: int) -> List[DBUser]:
        logger.info("Getting live users")
        return await self.users_collection.find({"isLive": True}).skip(offset).limit(limit).to_list(length=limit)

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

    async def remove_user_by_osu_id(self, osu_id: int):
        logger.info(f"Removing user by osu! id: {osu_id}")
        return await self.users_collection.delete_one({"osuId": osu_id})

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

    async def get_user_settings(self, osu_id: int):
        logger.info("Getting user settings...")
        default_settings = await self.get_default_settings()
        user = await self.users_collection.find_one({"osuId": osu_id})
        db_user = DBUser(**user)
        user_settings_dict = db_user.settings.dict(by_alias=True)

        for setting in default_settings:
            if user_settings_dict[setting.name] is not None:
                setting.value = user_settings_dict[setting.name]

        return default_settings

    async def update_user_settings(self, osu_id: int, settings: DBSetting):
        logger.info(f"Updating user settings: {settings}")
        return await self.users_collection.update_one(
            {"osuId": osu_id}, {"$set": {"settings": settings.dict(by_alias=True)}}
        )

    async def remove_excluded_user(self, osu_id: int, excluded_user: str):
        logger.info(f"Removing excluded user: {excluded_user}")
        return await self.users_collection.update_one(
            {"osuId": osu_id}, {"$pull": {"excludedUsers": excluded_user}}
        )

    async def add_excluded_user(self, osu_id: int, excluded_user: str):
        logger.info(f"Removing excluded user: {excluded_user}")
        return await self.users_collection.update_one(
            {"osuId": osu_id}, {"$addToSet": {"excludedUsers": excluded_user}}
        )

    async def get_excluded_users(self, osu_id: int):
        logger.info(f"Getting excluded users for: {osu_id}")
        user = await self.users_collection.find_one(
            {"osuId": osu_id}
        )
        return user["excludedUsers"]
