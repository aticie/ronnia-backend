from pydantic import BaseModel


class BaseStrippedUser(BaseModel):
    id: int


class StrippedOsuUser(BaseStrippedUser):
    username: str
    avatar_url: str


class StrippedTwitchUser(BaseStrippedUser):
    login: str
    profile_image_url: str
