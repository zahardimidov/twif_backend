from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import WEBAPP_URL

router = Router()

CURRENCY = 'XTR'
DONATE = '🚀 Продвижение проекта 🚀'


@router.message(CommandStart())
async def start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='Open 👀', web_app=WebAppInfo(url=WEBAPP_URL))
    )

    reply = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text=DONATE)
    ]], resize_keyboard=True)

    await message.answer('👋', reply_markup=reply)
    await message.answer('🤖 Hello from telegram bot\nYou can test mini app by clicking the button', reply_markup=builder.as_markup())