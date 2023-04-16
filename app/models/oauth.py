import datetime
from typing import Optional, List

from pydantic import BaseModel


class OauthBaseTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    obtained_epoch: int = datetime.datetime.now().timestamp()


class OsuOauthAuthorizationCodeTokenResponse(OauthBaseTokenResponse):
    scope: str = "identify"


class OsuOauthClientCredentialsTokenResponse(OauthBaseTokenResponse):
    scope: str = "public"


class TwitchOauthAuthorizationCodeTokenResponse(OauthBaseTokenResponse):
    scope: List[str]
