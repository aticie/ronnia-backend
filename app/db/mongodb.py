from typing import Optional, Union

from motor.motor_asyncio import AsyncIOMotorClient

from app.models.api import StrippedOsuUser, StrippedTwitchUser
from app.models.db import UserModel


class AsyncMongoClient(AsyncIOMotorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users_db = self.get_database("Ronnia")
        self.statistics_db = self.get_database("Ronnia-Statistics")
        self.users_collection = self.users_db.get_collection("Users")
        self.user_settings_collection = self.users_db.get_collection("UserSettings")
        self.settings_collection = self.users_db.get_collection("Settings")
        self.exclude_collection = self.users_db.get_collection("ExcludeList")

    async def get_user_from_twitch_id(self, twitch_id: int) -> UserModel:
        user = await self.users_collection.find_one({"twitch_id": str(twitch_id)})
        if user is not None:
            return UserModel(**user)

    async def get_user_from_osu_id(self, osu_id: int) -> UserModel:
        user = await self.users_collection.find_one({"osu_id": str(osu_id)})
        if user is not None:
            return UserModel(**user)

    async def insert_partial_user(
        self, user: Union[StrippedOsuUser, StrippedTwitchUser]
    ):
        return await self.users_collection.insert_one(user)

    async def update_user(self, user: dict):
        return await self.users_collection.update_one(
            {"_id": user["_id"]}, {"$set": user}
        )
