from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from api.schemas import *
from config import BOT_TOKEN
from database.requests import (complete_task, delete_user_wallet, set_user,
                               get_leaderboard, get_user_task, get_user_wallet,
                               get_users_ids, search_users, set_user, get_tasks,
                               set_user_wallet, users_complete_tasks)
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from middlewares import webapp_user_middleware
from ton_requests import get_account_nft, get_twif_balance

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.post('/create_user_just_test')
async def create_user_just_test(user: CreateUser):
    await set_user(user_id=user.id, username = user.username, fullname = user.fullname)

    return Response(status_code=200)


@router.get('/all', response_model=UsersList, include_in_schema=False)
async def get_all_users_ids():
    users = await get_users_ids()

    return UsersList(users=users)


@router.get('/search', response_model=SearchUsersResponse)
async def search_users_by_name(
    query: str = Query(...),
):
    users = await search_users(query=query)

    return dict(users=users)


@router.get('/leaderboard', response_model=LeaderboardResponse)
async def get_leaderboard_handler(
    limit: int = Query(...),
    offset: int = Query(default=0),
):
    leaders = await get_leaderboard(limit=limit, offset=offset)

    return dict(leaders=leaders)


@router.post('/me', response_model=UserResponse)
@webapp_user_middleware
async def me(request: WebAppRequest, initData: InitDataRequest):
    user = request.webapp_user
    return Response(status_code=200) # JSONResponse(status_code=200, content=jsonable_encoder(user))

@router.post('/ref', response_model=RefLinkResponse)
@webapp_user_middleware
async def get_ref_link(request: WebAppRequest, initData: InitDataRequest):
    link = await create_start_link(Bot(BOT_TOKEN), str(request.webapp_user.id), encode=True)

    return RefLinkResponse(link=link)


@router.post('/twif', response_model=UserTwifBalance)
@webapp_user_middleware
async def get_user_twif_balance(request: WebAppRequest, initData: InitDataRequest):
    wallet = await get_user_wallet(user_id=request.webapp_user.id)

    if wallet is None:
        raise HTTPException(status_code=400, detail='You should connect your wallet')
    
    balance = await get_twif_balance(wallet.address)

    return UserTwifBalance(twif=balance)


@router.post('/connect-wallet')
@webapp_user_middleware
async def connect_wallet(request: WebAppRequest, wallet: ConnectWalletRequest):
    user_id = request.webapp_user.id
    address = wallet.address

    await set_user_wallet(user_id=user_id, address=address)

    return JSONResponse(status_code=200, content=jsonable_encoder(dict(msg='Wallet was connected')))

@router.post('/disconnect-wallet')
@webapp_user_middleware
async def disconnect_wallet(request: WebAppRequest, initData: InitDataRequest):
    user_id = request.webapp_user.id

    await delete_user_wallet(user_id=user_id)

    return JSONResponse(status_code=200, content=jsonable_encoder(dict(msg='Wallet was disconnected')))


tasks_router = APIRouter(prefix='/tasks', tags=['Квесты'])


@tasks_router.get('/all', response_model=Tasks)
async def get_all_tasks():
    tasks = await get_tasks()

    return Tasks(tasks=[TaskResponse(id = task.id, text = task.text, url = task.url, reward=task.reward) for task in tasks])


@tasks_router.post('/complete')
@webapp_user_middleware
async def user_complete_task(request: WebAppRequest, task: UserCompleteTask):
    _task = await get_user_task(user_id=request.webapp_user.id, task_id=task.task_id)

    if not _task:
        completed_task = await complete_task(user_id=request.webapp_user.id, task_id=task.task_id)
        await set_user(user_id=request.webapp_user.id, points = request.webapp_user.points + completed_task.reward)

    return Response(status_code=200)

@tasks_router.post('/completed')
@webapp_user_middleware
async def user_completed_task(request: WebAppRequest, initData: InitDataRequest):
    tasks = await users_complete_tasks(user_id=request.webapp_user.id)

    return UserCompletedTasks(completed=[task.task_id for task in tasks])

