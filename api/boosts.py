from aiogram import Bot
from api.schemas import *
from config import BOT_TOKEN
from database.requests import (get_daily_boost, get_daily_boosts,
                               get_user_daily_boost, get_user_wallet, set_user,
                               set_user_daily_boost, get_referres, get_active_season)
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from middlewares import webapp_user_middleware
from ton_requests import get_account_nft, get_twif_balance

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
        raise HTTPException(status_code=400, detail='No daily boost selected')

    return JSONResponse(status_code=200, content=jsonable_encoder(daily_boost.boost))


@router.post('/set_user_daily_boost', response_model=DailyBoost)
@webapp_user_middleware
async def select_user_daily_boost(request: WebAppRequest, boost: SetUserDailyBoost):
    _boost = await get_daily_boost(boost_id=boost.boost_id)

    if request.webapp_user.stars < _boost.stars:
        raise HTTPException(
            status_code=400, detail='You do not have enough stars')

    await set_user_daily_boost(user_id=request.webapp_user.id, boost_id=boost.boost_id)
    await set_user(user_id=request.webapp_user.id, stars=request.webapp_user.stars - _boost.stars)

    return Response(status_code=200)


@router.post('/get_nft_boosts', response_model=UserBoostsForNFT)
@webapp_user_middleware
async def get_user_boosts_for_nft(request: WebAppRequest, initData: InitDataRequest):
    wallet = await get_user_wallet(user_id=request.webapp_user.id)

    if wallet is None:
        raise HTTPException(
            status_code=400, detail='You should connect your wallet')

    result = dict(white=1, black=1, silver=1, gold=1, result=1)
    extra = dict(white=1.1, black=1.4, silver=2.5, gold=10)
    nft_items = await get_account_nft(wallet.address)
    for nft in nft_items:
        result[nft['color']] *= extra[nft['color']]
        result['result'] *= extra[nft['color']]

    return UserBoostsForNFT(boosts=result)


MINUTES = 10

@router.post('/get_attempts')
@webapp_user_middleware
async def get_attempts(request: WebAppRequest, initData: InitDataRequest):
    if request.webapp_user.attempts < 6:
        dif = datetime.now(timezone.utc) - request.webapp_user.last_attempt
        dif: timedelta
        new_attempts = min(request.webapp_user.attempts + dif.seconds // (60 * MINUTES), 6)

        if new_attempts != request.webapp_user.attempts:
            la = datetime.now(timezone.utc) if request.webapp_user.last_attempt is None else request.webapp_user.last_attempt + timedelta(minutes=MINUTES)
            await set_user(user_id=request.webapp_user.id, attempts = new_attempts, last_attempt=la)

        return JSONResponse(status_code=200, content=jsonable_encoder({
            'attempts': new_attempts
        }))
    
    return JSONResponse(status_code=200, content=jsonable_encoder({'attempts': 6}))


@router.post('/save_game')
@webapp_user_middleware
async def save_game(request: WebAppRequest, game: SaveGame):
    if request.webapp_user.attempts == 6:
        await set_user(user_id=request.webapp_user.id, last_attempt=datetime.now(timezone.utc))

    await set_user(user_id=request.webapp_user.id, attempts = request.webapp_user.attempts - 1, points=request.webapp_user.points + game.points)

    referres = await get_referres(user=request.webapp_user)
    for i in range(len(referres)):
        bonus = int(game.points / 100 * (3-i))
        await set_user(user_id=referres[i], points=referres[i].points + bonus)

    return Response(status_code=200)


@router.get('/deadline')
async def get_deadline(request: Request):
    season = await get_active_season()

    if not season:
        raise HTTPException(status_code=404, detail='No one active season')

    deadline = season.deadline.strftime("%d.%m.%Y %H:%M")

    return JSONResponse(status_code=200, content=jsonable_encoder({
        'deadline': deadline
    }))