from typing import List, Tuple, Any

from pydantic import BaseModel


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
    settings: List[DBSetting] = []
    excludedUsers: List[str] = []
