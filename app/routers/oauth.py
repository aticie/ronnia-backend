from typing import Optional

from fastapi import APIRouter, Cookie
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.utils.login import OsuLoginHandler

router = APIRouter(prefix="/oauth2", tags=["oauth2"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/osu-login")
async def osu_oauth2_login(request: Request):
    login_handler = OsuLoginHandler(mongo_db=mongo_db)
    auth_url = login_handler.generate_auth_url(state=request.headers.get("referer"))
    return RedirectResponse(url=auth_url)


@router.get("/osu-redirect")
async def osu_oauth2_redirect(
    code: str, state: Optional[str] = None, signup_cookie: Optional[str] = Cookie(None)
):
    login_handler = OsuLoginHandler(mongo_db=mongo_db)
    db_user = await login_handler.get_user(code=code)
    redirect_response = RedirectResponse(url=state)
    if db_user:
        jwt_token = login_handler.create_user_jwt(db_user)
        redirect_response.set_cookie(key="token", value=jwt_token)
    else:
        jwt_token = login_handler.create_partial_user_jwt()
        redirect_response.set_cookie(
            key="signup",
            value="osu",
        )
        redirect_response.set_cookie(
            key="signup_details",
            value=jwt_token,
        )

    return redirect_response
