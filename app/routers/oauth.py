from typing import Optional, Union, Annotated

from fastapi import APIRouter, Cookie
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.utils.login import OsuLoginHandler, TwitchLoginHandler

router = APIRouter(prefix="/oauth2", tags=["oauth2"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/osu-login", summary="Redirects to the osu! OAuth page.")
async def osu_oauth2_login(request: Request):
    login_handler = OsuLoginHandler(mongo_db=mongo_db)
    auth_url = login_handler.generate_auth_url(state=request.headers.get("referer"))
    return RedirectResponse(url=auth_url)


@router.get("/osu-redirect", summary="Handles OAuth redirect from osu!.")
async def osu_oauth2_redirect(
    code: str,
    state: Optional[str] = None,
    signup_details: Annotated[str, Cookie()] = None,
):
    login_handler = OsuLoginHandler(mongo_db=mongo_db)
    login_handler.signup_cookie = signup_details
    redirect_response = await redirect_route(
        code=code, state=state, login_handler=login_handler
    )
    return redirect_response


@router.get("/twitch-login", summary="Redirects to the Twitch OAuth page.")
async def osu_oauth2_login(request: Request):
    login_handler = TwitchLoginHandler(mongo_db=mongo_db)
    auth_url = login_handler.generate_auth_url(state=request.headers.get("referer"))
    return RedirectResponse(url=auth_url)


@router.get("/twitch-redirect", summary="Handles OAuth redirect from Twitch.")
async def osu_oauth2_redirect(
    code: str,
    state: Optional[str] = None,
    signup_details: Annotated[str, Cookie()] = None,
):
    login_handler = TwitchLoginHandler(mongo_db=mongo_db)
    login_handler.signup_cookie = signup_details
    redirect_response = await redirect_route(
        code=code, state=state, login_handler=login_handler
    )
    return redirect_response


async def redirect_route(
    code: str, state: str, login_handler: Union[OsuLoginHandler, TwitchLoginHandler]
):
    redirect_response = RedirectResponse(url=state)
    db_user = await login_handler.get_user(code=code)
    if db_user:
        jwt_token = login_handler.create_user_jwt(db_user)
        redirect_response.set_cookie(key="signup", expires=0, max_age=0)
        redirect_response.set_cookie(key="signup_details", expires=0, max_age=0)
        redirect_response.set_cookie(key="token", value=jwt_token)
    else:
        jwt_token = login_handler.create_partial_user_jwt()
        redirect_response.set_cookie(
            key="signup",
            value="osu" if isinstance(login_handler, OsuLoginHandler) else "twitch",
        )
        redirect_response.set_cookie(
            key="signup_details",
            value=jwt_token,
        )
    return redirect_response
