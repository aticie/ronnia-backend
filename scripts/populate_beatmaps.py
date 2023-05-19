import asyncio

import aiohttp

from app.config import settings
from app.db.mongodb import AsyncMongoClient


async def get_access_token():
    url = "https://osu.ppy.sh/oauth/token"
    params = {
        "client_id": settings.OSU_CLIENT_ID,
        "client_secret": settings.OSU_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "public",
    }
    async with aiohttp.ClientSession() as sess:
        async with sess.post(url, json=params) as resp:
            token_response = await resp.json()

    return token_response["access_token"]


async def main():
    mongo_db = AsyncMongoClient(settings.MONGODB_URL)
    access_token = await get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    requested_beatmaps = await mongo_db.get_top_requested_beatmaps(
        limit=100000, offset=0
    )
    print(f"Found {len(requested_beatmaps)} beatmaps.")
    for beatmap_details in requested_beatmaps:
        beatmap_id = beatmap_details["_id"]

        db_beatmap = await mongo_db.beatmaps_collection.find_one({"id": beatmap_id})
        if db_beatmap is not None:
            print(f"Beatmap {beatmap_id} already exists.")
            continue

        beatmap_url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}"
        print(f"Fetching beatmap {beatmap_id}...")
        async with aiohttp.ClientSession(headers=headers) as sess:
            async with sess.get(beatmap_url) as resp:
                beatmap_resp = await resp.json()

        if "error" in beatmap_resp:
            print(f"Beatmap {beatmap_id} not found.")
            continue

        await mongo_db.beatmaps_collection.update_one(
            {"id": beatmap_id}, {"$set": beatmap_resp}, upsert=True
        )
        print(f"Beatmap {beatmap_id} added to database.")


if __name__ == "__main__":
    asyncio.run(main())
