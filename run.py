from api import party_router, users_router
from bot import process_update, run_bot_webhook
from middlewares import ImageCacheMiddleware, webapp_user_middleware
from config import BASE_DIR, WEBHOOK_PATH
from database.admin import init_admin
from database.session import engine, run_database
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from schemas import WebAppRequest
from utils import path_exists


async def on_startup(app: FastAPI):
    init_admin(app=app, engine=engine)
    await run_database()
    await run_bot_webhook()

    yield

app = FastAPI(lifespan=on_startup)
app.add_api_route('/'+WEBHOOK_PATH, endpoint=process_update, methods=['post'])
app.include_router(users_router)
app.include_router(party_router)

app.add_middleware(ImageCacheMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        '*'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', response_class=HTMLResponse)
@webapp_user_middleware
async def home(request: WebAppRequest):
    return f'<div style="display: flex; width: 100vw; height: 100vh; justify-content: center; background-color: #F9F9F9; color: #03527E;"> <b style="margin-top:35vh">Welcome!</b> </div>'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4550, forwarded_allow_ips='*')