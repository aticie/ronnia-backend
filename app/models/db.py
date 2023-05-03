from typing import List, Tuple

from pydantic import BaseModel, Field


class DBUserSettings(BaseModel):
    echo: bool
    enable: bool
    sub_only: bool = Field(alias='sub-only')
    points_only: bool = Field(alias='points-only')
    test: bool
    cooldown: float
    sr: Tuple[float, float]


class DBSetting(BaseModel):
    name: str
    value: float | Tuple[float, float]
    type: str
    description: str = ""


class DBUser(BaseModel):
    osuId: int
    osuUsername: str
    osuAvatarUrl: str = ""
    twitchId: int
    twitchUsername: str
    twitchAvatarUrl: str = ""
    excludedUsers: List[str] = []
    settings: dict = {}
