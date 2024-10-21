from aiogram import F, Router
from aiogram.types import (CallbackQuery, LabeledPrice, Message, InlineKeyboardButton,
                           PreCheckoutQuery)
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

CURRENCY = 'XTR'
DONATE = '🚀 Продвижение проекта 🚀'


def payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Pay 100 ⭐️', callback_data='donate_100'))
    builder.row(InlineKeyboardButton(text='Pay 200 ⭐️', callback_data='donate_200'))
    builder.row(InlineKeyboardButton(text='Pay 300 ⭐️', callback_data='donate_300'))

    return builder.as_markup()


@router.message(F.text == DONATE)
async def donate_keyboard(message: Message):
    await message.reply(text='Chose amount of Telegram Stars', reply_markup=payment_keyboard())


@router.callback_query()
async def donate(callback: CallbackQuery):
    amount = int(callback.data.split('_')[-1])

    prices = [
        LabeledPrice(label=CURRENCY, amount=amount),
    ]

    await callback.message.answer_invoice(
        title='Support and donate',
        description='Promoting the project through TelegramStars',
        prices=prices,
        provider_token="",
        payload="donate",
        currency=CURRENCY,
        reply_markup=InlineKeyboardBuilder().button(text=f'Pay {amount} ⭐️', pay=True).as_markup()
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    await message.answer(text=f'Successful payment {message.successful_payment.telegram_payment_charge_id} ⭐️', message_effect_id='5104841245755180586')
