from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.requests import get_user, set_user
from aiogram.utils.deep_linking import decode_payload

from config import BASE_DIR


async def extract_referral_id(message_text: str):
    try:
        payload = message_text.removeprefix('/start').strip()

        if not payload:
            raise Exception('No payload')

        payload_user_id = decode_payload(payload)
        referrer = await get_user(user_id=payload_user_id)
        return referrer.id
    except Exception as e:
        pass


class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str: Any],
    ) -> Any:

        if not event.chat.type == 'private':
            return

        user = await get_user(user_id=event.from_user.id)

        if not user:
            referrer_id = await extract_referral_id(event.text)
            photos = await event.bot.get_user_profile_photos(user_id=event.from_user.id)

            if photos.photos:
                photo = photos.photos[0][-1]

                file = await event.bot.get_file(photo.file_id)
                await event.bot.download_file(file.file_path, BASE_DIR.joinpath(f'media/avatars/{event.from_user.id}.png'))
            else:
                print('NO PHOTO')

            print('REFERRER_ID', referrer_id)
            user = await set_user(user_id=event.from_user.id, fullname=event.from_user.full_name, username=event.from_user.username, referrer_id=referrer_id)

        data['user'] = user

        return await handler(event, data)
