from fastapi import APIRouter

from app.config import settings
from app.db.mongodb import AsyncMongoClient

router = APIRouter(prefix="/requests", tags=["requests"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/beatmaps/top", summary="Shows top 5 requested beatmaps.")
async def top_beatmap_requests(n: int = 5):
    return await mongo_db.get_top_requested_beatmaps(limit=n, offset=0)
