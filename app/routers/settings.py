import logging

from fastapi import APIRouter

from app.config import settings
from app.db.mongodb import AsyncMongoClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/", summary="Gets Ronnia setting definitions from database")
async def get_settings():
    return await mongo_db.get_default_settings()
