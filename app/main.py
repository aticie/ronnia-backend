import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from app.config import settings
from app.routers import oauth, user, live, requests

logger = logging.getLogger(__name__)

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
)

if settings.DEBUG_MODE:
    app = FastAPI()
    origins = ["*"]
else:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    origins = [
        "https://ronnia.me",
        "https://www.ronnia.me",
        "https://staging.ronnia.me",
        "http://ronnia.me",
        "http://www.ronnia.me",
        "http://staging.ronnia.me",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth.router)
app.include_router(user.router)
app.include_router(live.router)
app.include_router(requests.router)
