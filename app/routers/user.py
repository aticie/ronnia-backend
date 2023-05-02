import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Cookie

from app.config import settings
from app.db.mongodb import AsyncMongoClient
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
async def get_user_details(user: Annotated[dict, Depends(decode_user_token)]):
    db_user = await mongo_db.remove_user_by_twitch_id(user["twitchId"])
    return db_user


@router.get("/logout", summary="Gets registered user details from database")
async def get_user_details(user: Annotated[dict, Depends(decode_user_token)]):
    pass
