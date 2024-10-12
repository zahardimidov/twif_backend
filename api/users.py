from database.requests import get_leaderboard
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schemas import *
from middlewares import webapp_user_middleware
from database.requests import get_user, get_leaderboard

router = APIRouter(tags=['Пользователи'])


@router.post('/me', response_model=UserResponse)
@webapp_user_middleware
async def me(request: WebAppRequest):
    me = await get_user(user_id=request.webapp_user.id)

    return me


@router.post('/balance', response_model=UserBalance)
@webapp_user_middleware
async def get_balance(request: WebAppRequest):
    data = jsonable_encoder({})

    return JSONResponse(content=data)


@router.get('/leaderboard', response_model=LeaderboardResponse)
async def get_leaderboard_handler(
    limit: int = Query(...),
    offset: int = Query(default=0),
):
    leaders = await get_leaderboard(limit=limit, offset=offset)

    return dict(leaders=leaders)
    
