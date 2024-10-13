from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from api.schemas import *
from config import BOT_TOKEN
from database.requests import get_leaderboard, get_user, search_users
from middlewares import webapp_user_middleware
from ton import get_twif_balance

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.get('/search', response_model=SearchUsersResponse)
async def search_users_by_name(
    query: str = Query(...),
):
    users = await search_users(query=query)

    return dict(users=users)


@router.get('/leaderboard', response_model=LeaderboardResponse)
async def get_leaderboard_handler(
    limit: int = Query(...),
    offset: int = Query(default=0),
):
    leaders = await get_leaderboard(limit=limit, offset=offset)

    return dict(leaders=leaders)


@router.post('/me', response_model=UserResponse)
@webapp_user_middleware
async def me(request: WebAppRequest, initData: InitDataRequest):
    me = await get_user(user_id=request.webapp_user.id)

    return me


@router.post('/ref', response_model=RefLinkResponse)
@webapp_user_middleware
async def get_ref_link(request: WebAppRequest, initData: InitDataRequest):
    link = await create_start_link(Bot(BOT_TOKEN), str(request.webapp_user.id), encode=True)

    return RefLinkResponse(link=link)


@router.post('/twif', response_model=UserTwifBalance)
@webapp_user_middleware
async def get_user_twif_balance(request: WebAppRequest, initData: InitDataRequest):
    balance = await get_twif_balance()

    return UserTwifBalance(twif=balance)
