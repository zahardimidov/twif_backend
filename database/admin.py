import json
import os

import redis
from config import ADMIN_PASSWORD, ADMIN_USERNAME
from database.models import (Button, Message, Party, PartyMember, StarsOffer, DailyBoost,
                             Transaction, User, Wallet, UserDailyBoost, Task, UserTaskCompleted)
from database.requests import get_users
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from markupsafe import Markup
from sqladmin import Admin, ModelView, action
from sqladmin.authentication import AuthenticationBackend
from middlewares.image_cache_middleware import cache

load_dotenv()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if not (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            return False

        request.session.update(
            {"token": "fdbb0dd1-a368-4689-bd71-5888f69b438e"})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token == 'fdbb0dd1-a368-4689-bd71-5888f69b438e':
            return False
        return True


authentication_backend = AdminAuth(secret_key="secret")

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.fullname, User.username,
                   User.points, User.stars, User.avatar]

    can_create = False
    can_edit = True

    form_widget_args_update = dict(
        id=dict(readonly=True), username=dict(readonly=True))

    column_formatters = {User.avatar: lambda m, a: Markup(
        f'<img style="height: 40px" src="{m.avatarURL}"/>')}

    name = 'Пользователь'
    name_plural = 'Пользователи'

    category = 'Пользователи'

class WalletAdmin(ModelView, model=Wallet):
    column_list = [Wallet.address, Wallet.user]
    form_columns = [Wallet.address, Wallet.user]

    name = 'Кошелек'
    name_plural = 'Кошельки'

    category = 'Пользователи'


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.wallet, Transaction.boc]

    can_create = False
    can_edit = False

    name = 'Транзакция'
    name_plural = 'Транзакции'

    category = 'Пользователи'


class UserDailyBoostAdmin(ModelView, model=UserDailyBoost):
    column_list = [UserDailyBoost.user, UserDailyBoost.boost, UserDailyBoost.date]

    name = 'Дневной буст пользователя'
    name_plural = 'Дневные бусты пользователя'

    category = 'Пользователи'

class TaskAdmin(ModelView, model=Task):
    column_list = [Task.text, Task.url, Task.reward]

    name = 'Квест'
    name_plural = 'Квесты'

class UserTasksCompletedAdmin(ModelView, model=UserTaskCompleted):
    column_list = [UserTaskCompleted.user, UserTaskCompleted.task, UserTaskCompleted.id]
    category = 'Пользователи'

    name = 'Выполненный квест'
    name_plural = 'Выполненные квесты'


class PartyAdmin(ModelView, model=Party):
    column_list = [Party.logo, Party.title, Party.quantity,
                   Party.nft_requirement, Party.twif_requirement, Party.id]

    column_formatters = {Party.logo: lambda m, a: showLogo(model=m)}

    name = 'Партия'
    name_plural = 'Партии'

    category = 'Партии'

    async def on_model_change(self, form: dict, model: Party, is_created: bool, request):
        try:
            if model.id == None:
                form['logo'] = None
            else:
                form['logo'].filename = model.generate_filename()
                del cache[form['logo'].filename]
        except Exception as e:
            print(e, request, model, form)

        await super(PartyAdmin, self).on_model_change(form, model, is_created, request)


def showLogo(model):
    filename = str(model.logo).split('/')[-1]

    return Markup(f'<img style="height: 40px" src="/media/logos/{filename}"/>')


class PartyMemberAdmin(ModelView, model=PartyMember):
    column_list = [PartyMember.party,
                   PartyMember.member, PartyMember.member_status]

    name = 'Участник партии'
    name_plural = 'Участники партий'

    category = 'Партии'


class StarsAdmin(ModelView, model=StarsOffer):
    column_list = [StarsOffer.amount, StarsOffer.ton, StarsOffer.id]

    name = 'Продажа Звезд'
    name_plural = 'Продажа Звезд'

    category = 'Товары'

class DailyBoostAdmin(ModelView, model=DailyBoost):
    column_list = [DailyBoost.multiplier, DailyBoost.stars, DailyBoost.nolimit, DailyBoost.id]

    name = 'Дневной буст'
    name_plural = 'Дневные бусты'

    category = 'Товары'


class ButtonAdmin(ModelView, model=Button):
    column_list = [Button.label, Button.url, Button.url]
    form_columns = ('label', 'url', 'message_id')

    name = 'Кнопка к сообщению'
    name_plural = 'Кнопки к сообщению'

    category = "Рассылка"


class MessageAdmin(ModelView, model=Message):
    form_columns = [Message.text, Message.photo, Message.buttons]

    column_list = [Message.text, Message.photo, Message.id]
    column_formatters = {Message.photo: lambda m, a: showPhoto(model=m)}

    name = 'Сообщение'
    name_plural = 'Сообщения'

    form_ajax_refs = {
        "buttons": {
            "fields": ("label", "url"),
            "order_by": "label",
        }
    }

    category = "Рассылка"

    async def on_model_change(self, form: dict, model: Message, is_created: bool, request):
        try:
            if model.id == None:
                form['photo'] = None
            else:
                form['photo'].filename = model.generate_filename()
                del cache[form['photo'].filename]
        except Exception as e:
            print(e, request, model, form)

        await super(MessageAdmin, self).on_model_change(form, model, is_created, request)

    @action('spread', 'Разослать сообщение')
    async def spread(self, request: Request):
        pks = request.query_params.get("pks", "").split(",")
        print(pks)
        if pks:
            for pk in pks:
                try:
                    r.rpush('spread_message', str(pk))
                except Exception as e:
                    print(e)

        referer = request.headers.get("Referer")
        if referer:
            return RedirectResponse(referer)
        else:
            return RedirectResponse(request.url_for("admin:list", identity=self.identity))


def showPhoto(model):
    if model.photo is None:
        return Markup('no photo')
    filename = str(model.photo).split('/')[-1]

    return Markup(f'<img style="height: 40px" src="/media/message/{filename}"/>')


def init_admin(app, engine):
    admin = Admin(app, engine=engine,
                  authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(WalletAdmin)
    admin.add_view(TransactionAdmin)
    admin.add_view(UserDailyBoostAdmin)
    admin.add_view(UserTasksCompletedAdmin)
    admin.add_view(TaskAdmin)

    admin.add_view(PartyAdmin)
    admin.add_view(PartyMemberAdmin)

    admin.add_view(StarsAdmin)
    admin.add_view(DailyBoostAdmin)

    admin.add_view(MessageAdmin)
    admin.add_view(ButtonAdmin)
