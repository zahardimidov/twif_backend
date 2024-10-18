from decimal import Decimal
from functools import wraps

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from api.schemas import *
from database.models import MemberStatusEnum, Party
from database.requests import (create_party, get_party, get_user, set_user,
                               get_user_party, get_user_vote, join_party, get_user_wallet)
from middlewares.webapp_user import webapp_user_middleware
from ton_requests import get_twif_balance, get_account_nft

router = APIRouter(prefix='/party', tags=['Партии'])


def validate_party_shares(party: Party):
    p = Decimal(str(party.founder_share)) + Decimal(str(party.members_share)) + \
        Decimal(str(party.project_share)) + Decimal(str(party.voters_share))
    if p != 1:
        raise HTTPException(
            status_code=400, detail='The sum of the distribution shares cannot differ from 1')


async def check_party_requirements(user_id, twif: int, nft: str):
    wallet = await get_user_wallet(user_id=user_id)

    if not wallet:
        raise HTTPException(f'User ({user_id}) should connect wallet')
    
    if twif and (await get_twif_balance(account_id=wallet.address)) < twif:
        raise HTTPException(f"User ({user_id}) doesn't have enought twif")
    
    if nft:
        user_nft = await get_account_nft(account_id=wallet.address)
        for nft in user_nft:
            if nft['color'] == nft:
                break
        else:
            raise HTTPException(f"User ({user_id}) doesn't have specific nft")
        
    return True




def without_party(func):
    @wraps(func)
    async def wrapper(request: WebAppRequest, *args, **kwargs):
        vote = await get_user_vote(user_id=request.webapp_user.id)

        if bool(vote):
            raise HTTPException(
                status_code=400, detail='You have already voted another party')

        party = await get_user_party(user_id=request.webapp_user.id)

        if bool(party):
            raise HTTPException(
                status_code=400, detail='You are already taking part in another party')

        return await func(request, *args, **kwargs)

    return wrapper


@router.post('/create', response_model=PartyResponse)
@webapp_user_middleware
@without_party
async def create_party_handler(request: WebAppRequest, party: PartyCreate = Depends(), logo: UploadFile = File(...)):
    data = dict(party)

    validate_party_shares(party)

    await check_party_requirements(user_id=request.webapp_user.id, twif=party.twif_requirement, nft=party.nft_requirement)

    party: Party = await create_party(logo=logo, **data)
    await join_party(party_id=party.id, user_id=request.webapp_user.id, status=MemberStatusEnum.creator)

    return JSONResponse(status_code=201, content=jsonable_encoder(data))


@router.post('/squad/create', response_model=PartyResponse)
@webapp_user_middleware
@without_party
async def create_squad_handler(request: WebAppRequest, party: SquadCreate = Depends(), logo: UploadFile = File(...)):
    data = dict(party)

    validate_party_shares(party)

    await check_party_requirements(user_id=request.webapp_user.id, twif=party.twif_requirement, nft=party.nft_requirement)

    for user_id in party.founder_ids:
        user = await get_user(user_id)

        if not user:
            raise HTTPException(
                status_code=400, detail=f'User with id {user_id} not found')
        
        if (await get_user_party(user_id=user.id)) is not None:
            raise HTTPException(
                status_code=400, detail=f'User with id {user_id} is already taking part in another party')
        
        await check_party_requirements(user_id=user_id, twif=party.twif_requirement, nft=party.nft_requirement)
    
    new_party: Party = await create_party(**data)
    await join_party(party_id=new_party.id, user_id=request.webapp_user.id, status=MemberStatusEnum.creator)

    for user_id in party.founder_ids:
        await join_party(party_id=new_party.id, user_id=user_id, status=MemberStatusEnum.founder)

    return JSONResponse(status_code=201, content=jsonable_encoder(data))


@router.post('/join')
@webapp_user_middleware
@without_party
async def join_party_handler(request: WebAppRequest, party: JoinPartyRequest):
    party: Party = await get_party(party_id=party.party_id)
    await check_party_requirements(user_id=request.webapp_user.id, twif=party.twif_requirement, nft=party.nft_requirement)
    await join_party(party_id=party.id, user_id=request.webapp_user.id)

    return JSONResponse(status_code=200, content=jsonable_encoder({
        'msg': 'success'
    }))


@router.post('/vote')
@webapp_user_middleware
@without_party
async def vote_party_handler(request: WebAppRequest, party: VotePartyRequest):
    await join_party(party_id=party.party_id, user_id=request.webapp_user.id)
    await set_user(points = 0)

    return Response(status_code=200)
