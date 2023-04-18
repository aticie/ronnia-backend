import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2, OAuth2AuthorizationCodeBearer

logger = logging.getLogger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://osu.ppy.sh/oauth/authorize",
    tokenUrl="https://osu.ppy.sh/oauth/token",
    scopes={
        "identify": "Identify your account",
        "public": "Access public information about your account",
    },
)


@router.get("/user_details", summary="Gets registered user details from database")
async def get_user_details(token: Annotated[str, Depends(oauth2_scheme)]):
    pass
