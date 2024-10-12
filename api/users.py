from database.requests import get_leaderboard
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schemas import *
from middlewares import webapp_user_middleware

router = APIRouter(tags=['Пользователи'])


@router.post('/me', response_model=UserResponse)
@webapp_user_middleware
async def me(request: WebAppRequest):
    data = jsonable_encoder({'party_id': request.webapp_user.id})

    return JSONResponse(content=data)

@router.post('/balance', response_model=UserBalance)
@webapp_user_middleware
async def get_balance(request: WebAppRequest):
    data = jsonable_encoder({})

    return JSONResponse(content=data)

@router.get('/leaderboard', response_model=LeaderboardResponse)
async def get_leaderboard(data: LeaderboardRequest):
    leaders = await get_leaderboard(limit=data.limit, offset=data.offset)

    print(leaders)

    return JSONResponse(content=jsonable_encoder({
        'leaders': leaders
    }))
