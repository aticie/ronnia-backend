import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Cookie

from app.utils.jwt import decode_jwt

logger = logging.getLogger(__name__)
router = APIRouter()


def decode_user_token(token: Annotated[str, Cookie()]):
    return decode_jwt(token)


@router.get("/user_details", summary="Gets registered user details from database")
async def get_user_details(user: Annotated[dict, Depends(decode_user_token)]):
    return user
