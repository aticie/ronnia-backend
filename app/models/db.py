from typing import List, Tuple, Optional

from pydantic import BaseModel, Field, validator


class DBUserSettings(BaseModel):
    echo: Optional[bool]
    enable: Optional[bool]
    sub_only: Optional[bool] = Field(alias='sub-only')
    points_only: Optional[bool] = Field(alias='points-only')
    test: Optional[bool]
    cooldown: Optional[float] = Field(None, ge=0)
    sr: Optional[Tuple[float, float]] = (0, -1)

    @validator('sr')
    def sr_must_be_in_range(cls, v):
        if v is not None:
            if v[0] < 0:
                raise ValueError("SR lower value must be positive.")
            elif v[1] != -1 and v[1] < v[0]:
                raise ValueError("SR max value must be higher than lower value.")
        return v


class DBSetting(BaseModel):
    name: str
    value: float | Tuple[float, float]
    type: str
    description: str = ""


class UserResponse(BaseModel):
    osuId: int
    osuUsername: str
    osuAvatarUrl: str = ""
    twitchId: int
    twitchUsername: str
    twitchAvatarUrl: str = ""
    excludedUsers: List[str] = []


class DBUser(UserResponse):
    settings: DBUserSettings = DBUserSettings()
