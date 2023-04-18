from abc import ABC
from typing import List, Dict, Any

import aiohttp

from app.models.oauth import (
    OsuOauthAuthorizationCodeTokenResponse,
    TwitchOauthAuthorizationCodeTokenResponse,
)


class BaseOAuthHandler:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: List[str] = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = " ".join(scopes) if scopes else ""
        self.auth_url = None
        self.token_url = None
        self.me_url = None

    def generate_auth_url(self, state: str = None) -> str:
        return (
            f"{self.auth_url}"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={self.scopes}"
            f"&state={state}"
        )

    async def get_oauth_token(self, code: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.token_url,
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            ) as response:
                return await response.json()


class OsuOAuthHandler(BaseOAuthHandler, ABC):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: List[str] = None,
    ):
        super().__init__(client_id, client_secret, redirect_uri, scopes)
        self.auth_url = "https://osu.ppy.sh/oauth/authorize"
        self.token_url = "https://osu.ppy.sh/oauth/token"

    async def get_oauth_token(
        self, code: str
    ) -> OsuOauthAuthorizationCodeTokenResponse:
        response = await super().get_oauth_token(code=code)
        return OsuOauthAuthorizationCodeTokenResponse(**response)


class TwitchOauthHandler(BaseOAuthHandler, ABC):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: List[str] = None,
    ):
        super().__init__(client_id, client_secret, redirect_uri, scopes)
        self.auth_url = "https://id.twitch.tv/oauth2/authorize"
        self.token_url = "https://id.twitch.tv/oauth2/token"

    async def get_oauth_token(
        self, code: str
    ) -> TwitchOauthAuthorizationCodeTokenResponse:
        response = await super().get_oauth_token(code=code)
        return TwitchOauthAuthorizationCodeTokenResponse(**response)
