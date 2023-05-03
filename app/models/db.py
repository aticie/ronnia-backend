from typing import List, Tuple, Any, Optional

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
    excludedUsers: List[str] = []
    settings: Optional[dict] = None
