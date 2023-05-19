import datetime

from fastapi import APIRouter

from app.config import settings
from app.db.mongodb import AsyncMongoClient

router = APIRouter(prefix="/requests", tags=["requests"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/beatmaps/top/daily", summary="Shows top requested beatmaps for today.")
async def top_beatmap_requests_day(limit: int = 5, offset: int = 0):
    time_start = datetime.datetime.today() - datetime.timedelta(days=1)
    return await mongo_db.get_top_requested_beatmaps(
        time_start=time_start, limit=limit, offset=offset
    )


@router.get(
    "/beatmaps/top/weekly", summary="Shows top requested beatmaps for this week."
)
async def top_beatmap_requests_week(limit: int = 5, offset: int = 0):
    time_start = datetime.datetime.today() - datetime.timedelta(days=30)
    return await mongo_db.get_top_requested_beatmaps(
        time_start=time_start, limit=limit, offset=offset
    )


@router.get(
    "/beatmaps/top/monthly", summary="Shows top requested beatmaps for this month."
)
async def top_beatmap_requests_month(limit: int = 5, offset: int = 0):
    time_start = datetime.datetime.today() - datetime.timedelta(days=30)
    return await mongo_db.get_top_requested_beatmaps(
        time_start=time_start, limit=limit, offset=offset
    )
