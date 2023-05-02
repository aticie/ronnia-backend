import asyncio
import logging
import os
import sqlite3
from typing import List

import aiohttp
from pymongo import UpdateOne

from app.db.mongodb import AsyncMongoClient
from app.models.db import DBUser, DBSetting

logger = logging.getLogger(__name__)


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


async def get_twitch_token():
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    params = {"client_id": client_id,
              "client_secret": client_secret,
              "grant_type": "client_credentials"}

    async with aiohttp.ClientSession() as sess:
        async with sess.post("https://id.twitch.tv/oauth2/token", json=params) as resp:
            result = await resp.json()

    return result["access_token"]


async def get_osu_token():
    client_id = os.getenv("OSU_CLIENT_ID")
    client_secret = os.getenv("OSU_CLIENT_SECRET")
    params = {"client_id": client_id,
              "client_secret": client_secret,
              "grant_type": "client_credentials",
              "scope": "public"}

    async with aiohttp.ClientSession() as sess:
        async with sess.post("https://osu.ppy.sh/oauth/token", json=params) as resp:
            result = await resp.json()

    return result["access_token"]


async def get_twitch_avatar_urls(twitch_ids: List[str]):
    avatars = {}
    token = await get_twitch_token()
    header = {"Authorization": f"Bearer {token}",
              "Client-Id": os.getenv("TWITCH_CLIENT_ID")}
    for ids in divide_chunks(twitch_ids, 100):
        params = {"id": ids}
        async with aiohttp.ClientSession(headers=header) as sess:
            async with sess.get("https://api.twitch.tv/helix/users", params=params) as r:
                resp = await r.json()

        for res in resp["data"]:
            avatars[res["id"]] = res["profile_image_url"]

    return avatars


async def get_osu_avatar_url(osu_id: str):
    token = await get_osu_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"key": "id"}
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.get(f"https://osu.ppy.sh/api/v2/users/{osu_id}", params=params) as r:
            resp = await r.json()

    if "error" in resp:
        logger.info(f"Errored on osu! avatar of {osu_id}")
        return ""
    logger.info(f"Got osu! avatar of {osu_id}")
    return resp["avatar_url"]


def add_users(old_db, new_db):
    users = old_db.execute("SELECT * FROM USERS;").fetchall()
    twitch_ids = [user["twitch_id"] for user in users]
    twitch_avatars = loop.run_until_complete(get_twitch_avatar_urls(twitch_ids))
    operations = []
    for user in users:
        user_id, osu_username, twitch_username, _, twitch_id, osu_id, _ = user.values()

        if twitch_id not in twitch_avatars:
            twitch_avatar = ""
        else:
            twitch_avatar = twitch_avatars[twitch_id]

        osu_id = int(osu_id)
        mongo_user: DBUser = loop.run_until_complete(new_db.get_user_from_osu_id(osu_id))
        if mongo_user is not None:
            logger.info(f"{mongo_user} already exists in database.")
            if mongo_user.twitchAvatarUrl == "" or mongo_user.osuAvatarUrl == "":
                logger.info(f"Found user {mongo_user} with no twitch avatar, deleting user...")
                loop.run_until_complete(new_db.remove_user_by_twitch_id(mongo_user.twitchId))
            continue

        osu_avatar = loop.run_until_complete(get_osu_avatar_url(osu_id))

        if osu_avatar == "" or twitch_avatar == "":
            continue

        db_user = DBUser(osuId=osu_id,
                         osuUsername=osu_username,
                         osuAvatarUrl=osu_avatar,
                         twitchId=twitch_id,
                         twitchUsername=twitch_username,
                         twitchAvatarUrl=twitch_avatar)
        logger.info(f"Adding {osu_username}/{twitch_username} to database.")
        operations.append(UpdateOne({"osuId": osu_id}, {"$set": db_user.dict()}, upsert=True))
    if len(operations) != 0:
        loop.run_until_complete(new_db.bulk_write_operations(operations))


def add_user_settings(old_db, new_db):
    logger.info("Adding user settings to database...")
    user_settings = old_db.execute(
        "SELECT * FROM user_settings INNER JOIN users ON users.user_id=user_settings.user_id;")
    user_range_settings = old_db.execute(
        "SELECT * FROM user_range_settings INNER JOIN users ON users.user_id=user_range_settings.user_id;")

    operations = []
    db_settings = {}
    for setting in user_settings:
        user_id = setting["osu_id"]
        setting_key = setting["key"]
        if setting_key == "cp-only":
            setting_key = "points-only"
        if user_id in db_settings:
            db_settings[user_id].update({setting_key: setting["value"]})
        else:
            db_settings[user_id] = {setting_key: setting["value"]}

    for setting in user_range_settings:
        user_id = setting["osu_id"]
        setting_key = setting["key"]
        value = setting["range_start"], setting["range_end"]
        if user_id in db_settings:
            db_settings[user_id].update({setting_key: value})
        else:
            db_settings[user_id] = {setting_key: value}

    logger.info(f"Found {len(db_settings)} users with settings.")
    for user_id, settings in db_settings.items():
        operations.append(UpdateOne({"osuId": int(user_id)}, {"$set": {"settings": settings}}))

    result = loop.run_until_complete(new_db.bulk_write_operations(operations))
    logger.info(f"Added {result.modified_count} settings to database.")


def add_settings(old_db, new_db):
    logger.info("Adding default settings to database...")
    settings = old_db.execute("SELECT * FROM settings;")
    range_settings = old_db.execute("SELECT * FROM range_settings;")
    operations = []
    for setting in settings:
        _id, name, value, description = setting.values()
        db_setting = DBSetting(name=name, value=value, description=description, type="value")
        UpdateOne({"name": db_setting.name}, {"$set": db_setting.dict()}, upsert=True)
        operations.append(UpdateOne({"name": db_setting.name}, {"$set": db_setting.dict()}, upsert=True))

    for setting in range_settings:
        _id, name, low_value, high_value, description = setting.values()
        db_setting = DBSetting(name=name, value=(low_value, high_value), description=description, type="range")
        UpdateOne({"name": db_setting.name}, {"$set": db_setting.dict()}, upsert=True)
        operations.append(UpdateOne({"name": db_setting.name}, {"$set": db_setting.dict()}, upsert=True))

    result = loop.run_until_complete(new_db.bulk_write_operations(operations, collection="Settings"))
    logger.info(f"Added {result.modified_count} settings to database.")


def add_exclude_list(old_db, new_db):
    logger.info("Adding exclude list to database...")
    exclude_list = old_db.execute("SELECT * FROM exclude_list INNER JOIN users u on exclude_list.user_id = u.user_id;")
    operations = []
    for user in exclude_list:
        user_id, excluded_users, osu_username, twitch_username, _, twitch_id, osu_id, _ = user.values()

        if excluded_users == "":
            continue
        excluded_users_list = excluded_users.split(",")
        logger.info(f"Adding {osu_username}/{twitch_username} to exclude list.")
        operations.append(UpdateOne({"osuId": int(osu_id)}, {"$set": {"excludedUsers": excluded_users_list}}, upsert=True))

    if len(operations) != 0:
        result = loop.run_until_complete(new_db.bulk_write_operations(operations))
        logger.info(f"Added {result.modified_count} users to exclude list.")


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    old_db = sqlite3.connect(os.getenv("DB_PATH"))
    old_db.row_factory = dict_factory
    new_db = AsyncMongoClient(os.getenv("MONGODB_URL"))

    loop = asyncio.get_event_loop()
    add_users(old_db, new_db)
    add_settings(old_db, new_db)
    add_user_settings(old_db, new_db)
    add_exclude_list(old_db, new_db)
