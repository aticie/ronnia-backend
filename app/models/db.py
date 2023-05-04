from typing import List, Tuple, Optional

from pydantic import BaseModel, Field, validator, conlist


class DBUserSettings(BaseModel):
    echo: bool = True
    enable: bool = True
    sub_only: bool = Field(False, alias='sub-only')
    points_only: bool = Field(False, alias='points-only')
    test: bool = False
    cooldown: float = Field(30, ge=0)
    sr: Optional[conlist(float, min_items=2, max_items=2)] = [0, -1]

    @validator('sr')
    def sr_must_be_in_range(cls, v):
        if v is not None:
            if v[0] < 0:
                raise ValueError("SR lower value must be positive.")
            elif v[1] != -1 and v[1] < v[0]:
                raise ValueError("SR max value must be higher than lower value.")
            elif v[1] >= 10:
                v[1] = -1
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
    isLive: bool = False


class DBUser(UserResponse):
    settings: DBUserSettings = DBUserSettings()
