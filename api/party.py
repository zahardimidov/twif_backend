from database.requests import create_party, get_user_vote, join_party
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from middlewares.webapp_user import webapp_user_middleware
from schemas import *

router = APIRouter(tags=['Партии'])


@router.post('/create_party', response_model=PartyResponse)
@webapp_user_middleware
async def create_party_handler(request: WebAppRequest, party: PartyCreate = Depends(), logo: UploadFile = File(...)):
    if party.founder_share + party.members_share + party.project_share + party.voters_share != 1:
        return JSONResponse(status_code=400, content=jsonable_encoder({
            'msg': 'Sharing parts should be equal 1'
        }))

    party = await create_party(creator_id=request.webapp_user.id, **party)

    return Response(status=201)


@router.post('/join_party')
@webapp_user_middleware
async def join_party_handler(request: WebAppRequest):
    data = await request.json()
    party_id = data['party_id']

    await join_party(party_id=party_id, user_id=request.webapp_user.id)

    return JSONResponse(content=jsonable_encoder(dict(result='ok')))


@router.post('/vote_party')
@webapp_user_middleware
async def vote_party_handler(request: WebAppRequest):
    data = await request.json()
    party_id = data['party_id']

    vote = await get_user_vote(user_id=request.webapp_user.id)

    if bool(vote):
        return JSONResponse(status_code=400, content=jsonable_encoder(dict(info='You have already voted another party')))

    await join_party(party_id=party_id, user_id=request.webapp_user.id)
    return JSONResponse(content=jsonable_encoder(dict(result='ok')))
