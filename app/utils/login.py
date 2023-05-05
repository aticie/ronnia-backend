from abc import ABC
from typing import Optional, Dict, Any, Union

import aiohttp
from fastapi.encoders import jsonable_encoder
from jose import jwt

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.models.api import StrippedTwitchUser, StrippedOsuUser
from app.models.db import DBUser as DBUserModel
from app.models.oauth import (
    TwitchOauthAuthorizationCodeTokenResponse,
    OsuOauthAuthorizationCodeTokenResponse,
)
from app.utils.jwt import obtain_jwt
from app.utils.oauth import OsuOAuthHandler, TwitchOauthHandler


class BaseLoginHandler:
    def __init__(
        self,
        mongo_db: Optional[AsyncMongoClient] = None,
    ):
        self._mongo_client: AsyncMongoClient = mongo_db
        self._api_field_mapping = {}
        self._auth_header = {}
        self._access_token = None
        self.api_user = None
        self._oauth_handler = None
        self._api = None
        self.db_user = None
        self.me_url = None
        self.signup_cookie = None

    def generate_auth_url(self, state: str = None):
        return self._oauth_handler.generate_auth_url(state)

    async def _get_user_from_token(self, access_token: str) -> Dict[str, Any]:
        self._auth_header["Authorization"] = f"Bearer {access_token}"
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            async with session.get(self.me_url) as response:
                return await response.json()

    async def _get_user_from_db(self, me_response: Dict[str, Any]):
        raise NotImplementedError

    async def _get_token(
        self, code: str
    ) -> Union[
        OsuOauthAuthorizationCodeTokenResponse,
        TwitchOauthAuthorizationCodeTokenResponse,
    ]:
        return await self._oauth_handler.get_oauth_token(code)

    async def get_user(self, code: str) -> Optional[DBUserModel]:
        access_token = await self._get_token(code)
        self.api_user = await self._get_user_from_token(access_token.access_token)
        if self.signup_cookie is not None:
            await self._upsert_user_to_db()
        self.db_user = await self._get_user_from_db(self.api_user)
        return self.db_user

    async def _upsert_user_to_db(self):
        raise NotImplementedError

    def create_partial_user_jwt(self):
        user_dict = self.api_user.dict(exclude_unset=True)
        return obtain_jwt(user_dict)

    def create_user_jwt(self, db_user: DBUserModel):
        return obtain_jwt(db_user.dict(exclude_unset=True))


class OsuLoginHandler(BaseLoginHandler):
    def __init__(self, mongo_db: AsyncMongoClient):
        super().__init__(mongo_db=mongo_db)
        self.me_url = "https://osu.ppy.sh/api/v2/me"
        self._oauth_handler = OsuOAuthHandler(
            settings.OSU_CLIENT_ID,
            settings.OSU_CLIENT_SECRET,
            settings.OSU_REDIRECT_URI,
            scopes=["identify"],
        )
        self.api_user: StrippedOsuUser

    async def _get_user_from_token(self, access_token: str) -> StrippedOsuUser:
        user_dict = await super()._get_user_from_token(access_token)
        return StrippedOsuUser(**user_dict)

    async def _get_user_from_db(self, osu_user: StrippedOsuUser) -> DBUserModel:
        osu_id = osu_user.id
        return await self._mongo_client.get_user_from_osu_id(osu_id)

    async def _upsert_user_to_db(self):
        user_partial_details = jwt.decode(self.signup_cookie, settings.JWT_SECRET_KEY)
        user_full_details = DBUserModel(
            osuId=self.api_user.id,
            osuUsername=self.api_user.username,
            osuAvatarUrl=self.api_user.avatar_url,
            twitchId=user_partial_details.get("id"),
            twitchUsername=user_partial_details.get("login"),
            twitchAvatarUrl=user_partial_details.get("profile_image_url"),
        )
        await self._mongo_client.upsert_user(user_full_details.dict())


class TwitchLoginHandler(BaseLoginHandler, ABC):
    def __init__(self, mongo_db: AsyncMongoClient):
        super().__init__(mongo_db=mongo_db)
        self.me_url = "https://api.twitch.tv/helix/users"
        self._oauth_handler = TwitchOauthHandler(
            settings.TWITCH_CLIENT_ID,
            settings.TWITCH_CLIENT_SECRET,
            settings.TWITCH_REDIRECT_URI,
            scopes=["user:read:email"],
        )
        self.api_user: StrippedTwitchUser

    async def _get_user_from_token(self, access_token: str) -> StrippedTwitchUser:
        self._auth_header["Client-Id"] = self._oauth_handler.client_id
        twitch_response = await super()._get_user_from_token(access_token)
        user_dict = twitch_response["data"][0]
        return StrippedTwitchUser(**user_dict)

    async def _get_user_from_db(self, twitch_user: StrippedTwitchUser) -> DBUserModel:
        twitch_id = twitch_user.id
        return await self._mongo_client.get_user_from_twitch_id(twitch_id)

    async def _upsert_user_to_db(self):
        user_partial_details = jwt.decode(self.signup_cookie, settings.JWT_SECRET_KEY)
        user_full_details = DBUserModel(
            twitchId=self.api_user.id,
            twitchUsername=self.api_user.login,
            twitchAvatarUrl=self.api_user.profile_image_url,
            osuId=user_partial_details.get("id"),
            osuUsername=user_partial_details.get("username"),
            osuAvatarUrl=user_partial_details.get("avatar_url"),
        )
        await self._mongo_client.upsert_user(user_full_details.dict())
