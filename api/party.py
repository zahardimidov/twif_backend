from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from database.models import MemberStatusEnum
from database.requests import create_party, get_user, get_user_vote, join_party
from middlewares.webapp_user import validate_data, webapp_user_middleware
from schemas import *

router = APIRouter(prefix='/party', tags=['Партии'])


@router.post('/create', response_model=PartyResponse)
async def create_party_handler(party: PartyCreate = Depends(), logo: UploadFile = File(...)):
    data = dict(party)
    user_data = validate_data(data.pop('initData'))

    if not user_data:
        return Response(status_code=400)
    

    if party.founder_share + party.members_share + party.project_share + party.voters_share != 1:
        return JSONResponse(status_code=400, content=jsonable_encoder({
            'msg': 'Sharing parts should be equal 1'
        }))

    party = await create_party(creator_id=user_data['id'], logo=logo, **data)
    print(logo.filename)

    return JSONResponse(status_code=201, content=jsonable_encoder(data))


@router.post('/squad/create', response_model=PartyResponse)
async def create_party_handler(squad: SquadCreate = Depends(), logo: UploadFile = File(...)):
    data = dict(squad)
    user_data = validate_data(data.pop('initData'))

    if not user_data:
        return Response(status_code=400)
    

    if squad.founder_share + squad.members_share + squad.project_share + squad.voters_share != 1:
        return JSONResponse(status_code=400, content=jsonable_encoder({
            'msg': 'Sharing parts should be equal 1'
        }))

    party = await create_party(creator_id=user_data['id'], **data)
    for user_id in squad.founder_ids:
        user = await get_user(user_id)

        if not user:
            return Response(status_code=400)

        await join_party(party_id=party.id, user_id=user_id, status=MemberStatusEnum.founder)

    return JSONResponse(status_code=201, content=jsonable_encoder(data))


@router.post('/join')
@webapp_user_middleware
async def join_party_handler(request: WebAppRequest):
    data = await request.json()
    party_id = data['party_id']

    await join_party(party_id=party_id, user_id=request.webapp_user.id)

    return Response(status=200)


@router.post('/vote')
@webapp_user_middleware
async def vote_party_handler(request: WebAppRequest):
    data = await request.json()
    party_id = data['party_id']

    vote = await get_user_vote(user_id=request.webapp_user.id)

    if bool(vote):
        return JSONResponse(status_code=400, content=jsonable_encoder(dict(info='You have already voted another party')))

    await join_party(party_id=party_id, user_id=request.webapp_user.id)

    return Response(status=200)
