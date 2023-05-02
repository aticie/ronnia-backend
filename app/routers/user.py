import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Cookie

from app.config import settings
from app.db.mongodb import AsyncMongoClient
from app.utils.jwt import decode_jwt

logger = logging.getLogger(__name__)
router = APIRouter()
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


def decode_user_token(token: Annotated[str, Cookie()]):
    return decode_jwt(token)


@router.get("/user_details", summary="Gets registered user details from database")
async def get_user_details(user: Annotated[dict, Depends(decode_user_token)]):
    db_user = await mongo_db.get_user_from_osu_id(user["osu_id"])
    return db_user
