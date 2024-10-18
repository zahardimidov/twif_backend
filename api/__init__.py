from api.boosts import router as boosts_router
from api.nft import router as nft_router
from api.party import router as party_router
from api.transaction import router as transaction_router
from api.users import router as users_router
from api.users import tasks_router

from database.requests import get_message_by_id
from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter(prefix='/messages', tags=['Cообщения'])


@router.get('/get', include_in_schema=False)
async def get_message(pk: str):
    if not pk:
        raise HTTPException('You need to provide pk')

    message = await get_message_by_id(message_id=pk)

    return JSONResponse(status_code=200, content=jsonable_encoder(dict(
        text=message.text,
        photo=message.photo,
        buttons=[
            {
                'label': button.label,
                'url': button.url
            } for button in message.buttons
        ]

    )))
