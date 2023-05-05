import logging
from typing import List

from fastapi import APIRouter

from app.config import settings
from app.db.mongodb import AsyncMongoClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/live", tags=["live"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/", summary="Gets currently streaming users.")
async def get_streaming_users(limit: int = 5, offset: int = 0) -> List[str]:
    users = await mongo_db.get_live_users(limit=limit, offset=offset)
    return [user.twitchUsername for user in users]
