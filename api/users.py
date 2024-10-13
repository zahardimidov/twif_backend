from database.requests import get_leaderboard
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schemas import *
from middlewares import webapp_user_middleware
from database.requests import get_user, get_leaderboard, search_users
from aiogram.utils.deep_linking import create_start_link
from aiogram import Bot
from ton import get_twif_balance
from config import BOT_TOKEN

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.post('/me', response_model=UserResponse)
@webapp_user_middleware
async def me(request: WebAppRequest):
    me = await get_user(user_id=request.webapp_user.id)

    return me

@router.get('/search', response_model=SearchUsersResponse)
async def search_users_by_name(
    query: str = Query(...),
):
    users = await search_users(query=query)
    
    return dict(users=users)

@router.post('/ref', response_model=UserRefLink)
@webapp_user_middleware
async def get_ref_link(request: WebAppRequest):
    link = await create_start_link(Bot(BOT_TOKEN), str(request.webapp_user.id), encode=True)

    return UserRefLink(link=link)


@router.post('/twif', response_model=UserTwifBalance)
@webapp_user_middleware
async def get_user_twif_balance(request: WebAppRequest):
    balance = await get_twif_balance()

    return UserTwifBalance(twif=balance)


@router.get('/leaderboard', response_model=LeaderboardResponse)
async def get_leaderboard_handler(
    limit: int = Query(...),
    offset: int = Query(default=0),
):
    leaders = await get_leaderboard(limit=limit, offset=offset)

    return dict(leaders=leaders)
    
