import hashlib
import hmac
import json
from functools import wraps
from operator import itemgetter
from urllib.parse import parse_qsl

from fastapi import HTTPException, Request

from api.schemas import WebAppRequest
from config import BOT_TOKEN, TEST_MODE, TEST_USER_ID, WEBHOOK_PATH
from database.requests import get_user


def validate_data(init_data: dict):
    try:
        hash_ = init_data.pop('hash')
        print(f'{hash_=}')
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(init_data.items(), key=itemgetter(0))
        )
        secret_key = hmac.new(
            key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256
        ).digest()
        calculated_hash = hmac.new(
            key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
        ).hexdigest()
        if calculated_hash == hash_:
            return json.loads(init_data['user'])
    except:
        if TEST_MODE:
            return {'id': TEST_USER_ID}

def findInitData(data: dict):
    print(f'kwargs={data}')

    for k, v in data.items():
        try:
            if isinstance(v.initData, bytes):
                s = v.initData.decode()
            elif isinstance(v.initData, str):
                s = v.initData
            
            del v.initData
            
            print(f'{s=}', f'\n{parse_qsl(s)=}', f'\ninitData={dict(parse_qsl(s))}')
            return dict(parse_qsl(s))
        except:pass
                

def webapp_user_middleware(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):            
        if str(request.url).endswith(WEBHOOK_PATH) or request.method == 'GET':
            return await func(request, *args, **kwargs)
        
        print(request)
        try: print((await request.json()))
        except:pass
        
        init_data = findInitData(kwargs)

        if init_data is None:
            raise HTTPException(status_code=400, detail='Provide correct initData')
        
        user_data = validate_data(init_data)
        print(f'{user_data=}')
        if user_data:
            user = await get_user(user_id=user_data['id'])

            if not user:
                raise HTTPException(status_code=404, detail= 'User profile not found')

            webapp_request = WebAppRequest(
                webapp_user=user, **request.__dict__)

            return await func(webapp_request, *args, **kwargs)

        raise HTTPException(status_code=401, detail= 'Open this page from TelegramMiniApp')

    return wrapper
