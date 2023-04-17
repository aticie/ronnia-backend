import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.routers import oauth

logger = logging.getLogger(__name__)

if settings.DEBUG_MODE:
    app = FastAPI()
    origins = ["*"]
else:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    origins = ["ronnia.me", "www.ronnia.me", "api.ronnia.me"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth.router)


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
