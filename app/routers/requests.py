import datetime

from fastapi import APIRouter

from app.config import settings
from app.db.mongodb import AsyncMongoClient

router = APIRouter(prefix="/requests", tags=["requests"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get(
    "/beatmaps/top", summary="Shows top requested beatmaps for the selected time."
)
async def top_beatmap_requests_day(days_ago: int = 1, limit: int = 5, offset: int = 0):
    time_start = datetime.datetime.today() - datetime.timedelta(days=days_ago)
    return await mongo_db.get_top_requested_beatmaps(
        time_start=time_start, limit=limit, offset=offset
    )
