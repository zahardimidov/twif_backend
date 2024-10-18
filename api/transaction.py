from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from api.schemas import *
from middlewares import webapp_user_middleware
from ton_requests import getLastByBoc
from database.requests import get_user_wallet, get_transaction, get_stars_offer, get_stars_offers, set_user

router = APIRouter(prefix='/stars', tags=['Звезды'])

@router.get('/offers', response_model=StarsOffers)
async def offers():
    offers = await get_stars_offers()

    return StarsOffers(offers=offers)

@router.post('/topup')
@webapp_user_middleware
async def topup_stars(request: WebAppRequest, transaction: StarsTransaction):
    wallet = await get_user_wallet(user_id=request.webapp_user.id) 

    if not wallet:
        raise HTTPException(status_code=400, detail='Connect your wallet please')
    
    _transaction = await get_transaction(boc = transaction.boc)
    if _transaction:
        raise HTTPException(status_code=400, detail='You have already saved transaction with this boc')
    
    transaction = await getLastByBoc(address=wallet.address, boc=transaction.boc)

    value = transaction['in_msg']['value']
    offer_id = transaction.offer_id

    offer = await get_stars_offer(offer_id=offer_id)
    if offer and offer.ton == value:
        await set_user(user_id=request.webapp_user.id, stars = request.webapp_user.stars + offer.amount)
        return Response(status_code=200)
    
    raise HTTPException(status_code=400, detail='No one offer mathes with your transaction')
 

