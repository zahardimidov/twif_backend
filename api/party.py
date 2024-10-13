from decimal import Decimal
from functools import wraps

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from api.schemas import *
from database.models import MemberStatusEnum, Party
from database.requests import (create_party, get_party_member, get_user,
                               get_user_party, get_user_vote, join_party)
from middlewares.webapp_user import webapp_user_middleware

router = APIRouter(prefix='/party', tags=['Партии'])


def validate_party(party: Party):
    p = Decimal(str(party.founder_share)) + Decimal(str(party.members_share)) + \
        Decimal(str(party.project_share)) + Decimal(str(party.voters_share))
    if p != 1:
        raise HTTPException(
            status_code=400, detail='The sum of the distribution shares cannot differ from 1')


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

    validate_party(party)

    await create_party(creator_id=request.webapp_user.id, logo=logo, **data)

    return JSONResponse(status_code=201, content=jsonable_encoder(data))


@router.post('/squad/create', response_model=PartyResponse)
@webapp_user_middleware
@without_party
async def create_squad_handler(request: WebAppRequest, party: SquadCreate = Depends(), logo: UploadFile = File(...)):
    data = dict(party)

    validate_party(party)

    party = await create_party(creator_id=request.webapp_user.id, **data)
    for user_id in party.founder_ids:
        user = await get_user(user_id)

        if not user:
            return Response(status_code=400)

        await join_party(party_id=party.id, user_id=user_id, status=MemberStatusEnum.founder)

    return JSONResponse(status_code=201, content=jsonable_encoder(data))


@router.post('/join')
@webapp_user_middleware
@without_party
async def join_party_handler(request: WebAppRequest, party: JoinPartyRequest):
    await join_party(party_id=party.party_id, user_id=request.webapp_user.id)

    return JSONResponse(status_code=200, content=jsonable_encoder({
        'msg': 'success'
    }))


@router.post('/vote')
@webapp_user_middleware
@without_party
async def vote_party_handler(request: WebAppRequest, party: VotePartyRequest):
    await join_party(party_id=party.party_id, user_id=request.webapp_user.id)

    return Response(status_code=200)
