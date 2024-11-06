from api import (boosts_router, nft_router, party_router, router, tasks_router,
                 transaction_router, users_router)
from bot import process_update, run_bot_webhook
from config import BASE_DIR, PORT, WEBHOOK_PATH
from database.admin import init_admin
from database.session import engine, run_database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from middlewares import ImageCacheMiddleware


async def on_startup(app: FastAPI):
    init_admin(app=app, engine=engine)
    await run_database()
    await run_bot_webhook()

    yield

app = FastAPI(lifespan=on_startup)
app.mount(
    "/static", StaticFiles(directory=BASE_DIR.joinpath('static')), name="static")
app.add_api_route('/'+WEBHOOK_PATH, endpoint=process_update,
                  methods=['post'], include_in_schema=False)
app.include_router(router)
app.include_router(users_router)
app.include_router(boosts_router)
app.include_router(tasks_router)
app.include_router(party_router)
app.include_router(nft_router)
app.include_router(transaction_router)

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


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def home():
    return f'<div style="display: flex; width: 100vw; height: 100vh; justify-content: center; background-color: #F9F9F9; color: #03527E;"> <b style="margin-top:35vh">Welcome!</b> </div>'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, forwarded_allow_ips='*')
