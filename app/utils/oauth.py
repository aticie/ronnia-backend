import urllib.parse
from typing import List

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

    def generate_auth_url(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scopes,
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    async def get_token(self, code: str):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        async with aiohttp.ClientSession() as temp_session:
            async with temp_session.post(self.token_url, json=data) as resp:
                response = await resp.json()

        return response


class OsuOAuthHandler(BaseOAuthHandler):
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

    async def get_token(self, code: str):
        response = await super().get_token(code)
        return OsuOauthAuthorizationCodeTokenResponse(**response)


class TwitchOauthHandler(BaseOAuthHandler):
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

    async def get_token(self, code: str):
        response = await super().get_token(code)
        return TwitchOauthAuthorizationCodeTokenResponse(**response)
