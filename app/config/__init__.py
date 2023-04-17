from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    APP_NAME: str = "Ronnia"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"


class ServerSettings(BaseSettings):
    PUBLISH_HOST: str = "0.0.0.0"
    PUBLISH_PORT: int = 8000


class DatabaseSettings(BaseSettings):
    MONGODB_URL: str


class APISettings(BaseSettings):
    OSU_CLIENT_ID: str
    OSU_CLIENT_SECRET: str
    OSU_REDIRECT_URI: str
    TWITCH_CLIENT_ID: str
    TWITCH_CLIENT_SECRET: str
    TWITCH_REDIRECT_URI: str


class Settings(CommonSettings, ServerSettings, DatabaseSettings, APISettings):
    pass


settings = Settings()
