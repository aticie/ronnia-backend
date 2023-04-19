from abc import ABC
from typing import Optional, Dict, Any, Union

import aiohttp
from jose import jwt

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.models.api import StrippedTwitchUser, StrippedOsuUser
from app.models.db import UserModel as DBUserModel
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
        auth_header = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession(headers=auth_header) as session:
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
            await self._insert_user_to_db()
        self.db_user = await self._get_user_from_db(self.api_user)
        return self.db_user

    async def _insert_user_to_db(self):
        raise NotImplementedError

    def create_partial_user_jwt(self):
        return obtain_jwt(self.api_user.dict(exclude_unset=True))

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

    async def _insert_user_to_db(self):
        user_partial_details = jwt.decode(self.signup_cookie, settings.SECRET_KEY)
        user_full_details = DBUserModel(
            osu_id=self.api_user.id,
            osu_username=self.api_user.username,
            osu_avatar_url=self.api_user.avatar_url,
            twitch_id=user_partial_details.get("id"),
            twitch_username=user_partial_details.get("login"),
            twitch_avatar_url=user_partial_details.get("profile_image_url"),
        )

        await self._mongo_client.insert_user(user_full_details)

    async def _get_user_from_token(self, access_token: str) -> StrippedOsuUser:
        user_dict = await super()._get_user_from_token(access_token)
        return StrippedOsuUser(**user_dict)

    async def _get_user_from_db(self, osu_user: StrippedOsuUser) -> DBUserModel:
        osu_id = osu_user.id
        return await self._mongo_client.get_user_from_osu_id(osu_id)


class TwitchLoginHandler(BaseLoginHandler, ABC):
    def __init__(self, mongo_db: AsyncMongoClient):
        super().__init__(mongo_db=mongo_db)
        self.me_url = "https://api.twitch.tv/helix/users"
        self.oauth_handler = TwitchOauthHandler(
            settings.TWITCH_CLIENT_ID,
            settings.TWITCH_CLIENT_SECRET,
            settings.TWITCH_REDIRECT_URI,
            scopes=["user:read:email"],
        )
        self.api_user: StrippedTwitchUser

    async def _insert_user_to_db(self):
        user_partial_details = jwt.decode(self.signup_cookie, settings.SECRET_KEY)
        user_full_details = DBUserModel(
            twitch_id=self.api_user.id,
            twitch_username=self.api_user.login,
            twitch_avatar_url=self.api_user.profile_image_url,
            osu_id=user_partial_details.get("id"),
            osu_username=user_partial_details.get("username"),
            osu_avatar_url=user_partial_details.get("avatar_url"),
        )

        await self._mongo_client.insert_user(user_full_details)

    async def _get_user_from_token(self, access_token: str) -> StrippedTwitchUser:
        user_dict = await super()._get_user_from_token(access_token)
        return StrippedTwitchUser(**user_dict)

    async def _get_user_from_db(self, twitch_user: StrippedTwitchUser) -> DBUserModel:
        twitch_id = twitch_user.id
        return await self._mongo_client.get_user_from_twitch_id(twitch_id)
