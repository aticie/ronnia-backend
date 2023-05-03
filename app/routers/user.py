import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Cookie
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response
from pymongo.results import DeleteResult

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.models.db import DBUserSettings
from app.utils.jwt import decode_jwt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["user"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


def decode_user_token(token: Annotated[str, Cookie()]):
    return decode_jwt(token)


@router.get("/me", summary="Gets registered user details from database")
async def get_user_details(user: Annotated[dict, Depends(decode_user_token)]):
    db_user = await mongo_db.get_user_from_osu_id(user["osuId"])
    return db_user


@router.delete("/me", summary="Deletes the registered user from database")
async def remove_user(user: Annotated[dict, Depends(decode_user_token)],
                      request: Request):
    await mongo_db.remove_user_by_twitch_id(user["twitchId"])
    response = RedirectResponse(url=request.headers.get("referer"))
    response.set_cookie("token", expires=0, max_age=0)
    return response


@router.get("/settings", summary="Gets user settings from database")
async def get_settings(user: Annotated[dict, Depends(decode_user_token)]):
    return await mongo_db.get_user_settings(user["osuId"])


@router.post("/settings", summary="Post user settings to database")
async def get_settings(user: Annotated[dict, Depends(decode_user_token)],
                       user_settings: dict):
    await mongo_db.update_user_settings(user["osuId"], DBUserSettings(**user_settings))
