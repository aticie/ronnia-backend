from pydantic import BaseModel


class UserModel(BaseModel):
    osu_id: int
    osu_username: str
    osu_avatar: str = ""
    twitch_id: int
    twitch_username: str
    twitch_avatar: str = ""
