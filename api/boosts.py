from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from api.schemas import *
from config import BOT_TOKEN
from database.requests import get_daily_boost, get_user_wallet, get_daily_boosts, get_user_daily_boost, set_user_daily_boost, set_user
from middlewares import webapp_user_middleware
from ton_requests import get_twif_balance, get_account_nft

router = APIRouter(prefix='/boosts', tags=['Бусты и Игра'])


@router.get('/daily', response_model=AllDailyBoost)
async def get_all_daily_boosts():
    boosts = await get_daily_boosts()
    return JSONResponse(status_code=200, content=jsonable_encoder(boosts))

@router.post('/user_daily_boost', response_model=DailyBoost)
@webapp_user_middleware
async def get_user_boosts_for_nft(request: WebAppRequest, initData: InitDataRequest):
    daily_boost = await get_user_daily_boost(user_id=request.webapp_user.id)

    if daily_boost is None:
        raise HTTPException(status_code=400, detail= 'No daily boost selected')

    return JSONResponse(status_code=200, content=jsonable_encoder(daily_boost.boost))

@router.post('/set_user_daily_boost', response_model=DailyBoost)
@webapp_user_middleware
async def select_user_daily_boost(request: WebAppRequest, boost: SetUserDailyBoost):
    _boost = await get_daily_boost(boost_id=boost.boost_id)

    if request.webapp_user.stars < _boost.stars:
        raise HTTPException(status_code=400, detail='You do not have enough stars')
    
    await set_user_daily_boost(user_id=request.webapp_user.id, boost_id=boost.boost_id)
    await set_user(user_id=request.webapp_user.id, stars = request.webapp_user.stars - _boost.stars)

    return Response(status_code=200)
    

@router.post('/get_nft_boosts', response_model=UserBoostsForNFT)
@webapp_user_middleware
async def get_user_boosts_for_nft(request: WebAppRequest, initData: InitDataRequest):
    wallet = await get_user_wallet(user_id=request.webapp_user.id)

    if wallet is None:
        raise HTTPException(status_code=400, detail='You should connect your wallet')
    
    result = dict(white = 1, black = 1, silver = 1, gold = 1)
    extra = dict(white = 1.1, black = 1.4, silver = 2.5, gold = 10)
    nft_items = await get_account_nft(wallet.address)
    for nft in nft_items:
        result[nft['color']] *= extra[nft['color']]

    return UserBoostsForNFT(boosts=result)
    

@router.post('/topup_attempts', response_model=UserResponse)
@webapp_user_middleware
async def topup_attempts(request: WebAppRequest, initData: InitDataRequest):
    if request.webapp_user.last_attempt is not None and request.webapp_user.last_attempt < datetime.now(timezone.utc) - timedelta(minutes=10):
        return Response(status = 200)

    return Response(status = 400)


@router.post('/save_game', response_model=UserResponse)
async def save_game(request: WebAppRequest, game: SaveGame):
    await set_user(user_id=request.webapp_user.id, last_attempt = datetime.now(timezone.utc), points = request.webapp_user.points + game.points)

    return Response(status_code=200)


