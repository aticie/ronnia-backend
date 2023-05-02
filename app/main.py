import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import oauth, user

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
app.include_router(user.router)
