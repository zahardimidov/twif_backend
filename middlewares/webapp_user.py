import hashlib
import hmac
import json
from operator import itemgetter
from urllib.parse import parse_qsl

from fastapi import HTTPException, Request

from config import BOT_TOKEN, WEBHOOK_PATH, TEST_MODE, TEST_USER_ID
from database.requests import get_user
from schemas import WebAppRequest

from functools import wraps


def validate_data(init_data):
    try:
        parsed_data = dict(parse_qsl(init_data))
        hash_ = parsed_data.pop('hash')
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
        )
        secret_key = hmac.new(
            key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256
        ).digest()
        calculated_hash = hmac.new(
            key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
        ).hexdigest()
        if calculated_hash == hash_:
            return json.loads(parsed_data['user'])
    except:
        if TEST_MODE:
            return {'id': TEST_USER_ID}


def webapp_user_middleware(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if str(request.url).endswith(WEBHOOK_PATH) or request.method == 'GET':
            return await func(request, *args, **kwargs)

        error_text = 'Open this page from telegram'

        body = await request.body()
        data: dict = json.loads(body.decode())
        init_data = data.get('initData')

        if user_data:=validate_data(init_data):
            user = await get_user(user_id=user_data['id'])

            webapp_request = WebAppRequest(
                webapp_user=user, **request.__dict__)

            return await func(webapp_request, *args, **kwargs)
        
        return HTTPException(status_code=401, detail=error_text)

    return wrapper
