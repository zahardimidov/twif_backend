from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import Request

from middlewares import RegisterUserMiddleware
from bot.routers import base_router
from config import BOT_TOKEN, WEBHOOK_HOST, WEBHOOK_PATH


async def run_bot_webhook():
    me = await bot.get_me()
    print(me.username)

    await bot.set_webhook(f'{WEBHOOK_HOST}/{WEBHOOK_PATH}', drop_pending_updates=True)


async def run_bot_polling():
    me = await bot.get_me()
    print(me.username)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(base_router)
dp.message.middleware(RegisterUserMiddleware())


async def process_update(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
