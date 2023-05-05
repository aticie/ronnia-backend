import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Cookie
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.models.db import DBUserSettings, UserResponse
from app.utils.jwt import decode_jwt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["user"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


def decode_user_token(token: Annotated[str, Cookie()]):
    return decode_jwt(token)


@router.get("/me", summary="Gets registered user details from database")
async def get_user_details(user: Annotated[dict, Depends(decode_user_token)]):
    db_user = await mongo_db.get_user_from_osu_id(user["osuId"])
    return UserResponse(**db_user.dict())


@router.delete("/me", summary="Deletes the registered user from database")
async def remove_user(
    user: Annotated[dict, Depends(decode_user_token)], request: Request
):
    await mongo_db.remove_user_by_twitch_id(user["twitchId"])
    response = RedirectResponse(url=request.headers.get("referer"))
    response.set_cookie("token", expires=0, max_age=0, secure=True, httponly=True)
    return response


@router.get("/settings", summary="Gets user settings from database")
async def get_settings(user: Annotated[dict, Depends(decode_user_token)]):
    return await mongo_db.get_user_settings(user["osuId"])


@router.post("/settings", summary="Post user settings to database")
async def post_settings(
    user: Annotated[dict, Depends(decode_user_token)], user_settings: DBUserSettings
):
    await mongo_db.update_user_settings(user["osuId"], user_settings)


@router.get("/exclude", summary="Get a user's excluded users list")
async def get_excluded_users(user: Annotated[dict, Depends(decode_user_token)]):
    excluded_list = await mongo_db.get_excluded_users(user["osuId"])
    return excluded_list


@router.post("/exclude", summary="Adds an excluded user to user's list")
async def add_excluded_user(
    user: Annotated[dict, Depends(decode_user_token)], excluded_user: str
):
    await mongo_db.add_excluded_user(user["osuId"], excluded_user)
    return excluded_user


@router.delete("/exclude", summary="Adds an excluded user to user's list")
async def remove_excluded_user(
    user: Annotated[dict, Depends(decode_user_token)], excluded_user: str
):
    await mongo_db.remove_excluded_user(user["osuId"], excluded_user)
    return excluded_user
