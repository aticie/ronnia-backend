from abc import ABC
from typing import Optional, Dict, Any, Union

import aiohttp
import aiosu
from jose import jwt

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.models.api import StrippedTwitchUser, StrippedOsuUser
from app.models.db import UserModel
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
        self._mongo_client = mongo_db
        self._access_token = None
        self.api_user = None
        self._oauth_handler = None
        self._api = None
        self.db_user = None
        self.me_url = None

    def generate_auth_url(self, state: str = None):
        return self._oauth_handler.generate_auth_url(state)

    async def get_user_from_token(self, access_token: str) -> Dict[str, Any]:
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

    async def get_user(self, code: str) -> Optional[UserModel]:
        access_token = await self._get_token(code)
        self.api_user = await self.get_user_from_token(access_token.access_token)
        self.db_user = await self._get_user_from_db(self.api_user)
        return self.db_user

    def create_partial_user_jwt(self):
        return obtain_jwt(self.api_user.dict(exclude_unset=True))

    def create_user_jwt(self, db_user: UserModel):
        obtain_jwt(db_user.dict(exclude_unset=True))


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

    async def get_user_from_token(self, access_token: str) -> StrippedOsuUser:
        user_dict = await super().get_user_from_token(access_token)
        return StrippedOsuUser(**user_dict)

    async def _get_user_from_db(self, osu_user: StrippedOsuUser) -> UserModel:
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

    async def get_user_from_token(self, access_token: str) -> StrippedTwitchUser:
        user_dict = await super().get_user_from_token(access_token)
        return StrippedTwitchUser(**user_dict)

    async def _get_user_from_db(self, twitch_user: StrippedTwitchUser) -> UserModel:
        twitch_id = twitch_user.id
        return await self._mongo_client.get_user_from_twitch_id(twitch_id)
