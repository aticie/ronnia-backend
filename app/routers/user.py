import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/user_details", summary='Gets registered user details from database')
async def get_user_details(jwt_token: str):
    pass
