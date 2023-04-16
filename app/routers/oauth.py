from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.config import settings
from app.utils.oauth import TwitchOauthHandler, OsuOAuthHandler

router = APIRouter(prefix="/oauth2")
osu_oauth_handler = OsuOAuthHandler(
    settings.OSU_CLIENT_ID,
    settings.OSU_CLIENT_SECRET,
    settings.OSU_REDIRECT_URI,
    scopes=["identify"],
)

twitch_oauth_handler = TwitchOauthHandler(
    settings.TWITCH_CLIENT_ID,
    settings.TWITCH_CLIENT_SECRET,
    settings.TWITCH_REDIRECT_URI,
    scopes=["user:read:email"],
)


@router.get("/osu-login")
async def osu_oauth2_login():
    url = osu_oauth_handler.generate_auth_url()
    return RedirectResponse(url=url)


@router.get("/osu-redirect")
async def osu_oauth2_redirect(code: str):
    osu_access_token = await osu_oauth_handler.get_token(code)
    return osu_access_token


@router.get("/twitch-login")
async def twitch_oauth2_login():
    url = twitch_oauth_handler.generate_auth_url()
    return RedirectResponse(url=url)


@router.get("/twitch-redirect")
async def twitch_oauth2_redirect(code: str):
    twitch_access_token = await twitch_oauth_handler.get_token(code)
    return twitch_access_token
