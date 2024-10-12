from fastapi import Request
from fastapi.responses import RedirectResponse
from markupsafe import Markup
from sqladmin import Admin, ModelView, action
from sqladmin.authentication import AuthenticationBackend

from config import ADMIN_PASSWORD, ADMIN_USERNAME
from database.models import User, Party, PartyMember


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


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.fullname, User.username,
                   User.points, User.stars, User.avatar]

    column_formatters = {User.avatar: lambda m, a: Markup(
        f'<img style="height: 40px" src="{m.avatarURL}"/>')}

    '''@action('copy', 'Copy Item', 'Are you sure you want to copy this item?')    
    async def copy_action(self, request: Request):
        pks = request.query_params.get("pks", "").split(",")
        if pks:
            for pk in pks:
                await copy_user(int(pk))

        referer = request.headers.get("Referer")
        if referer:
            return RedirectResponse(referer)
        else:
            return RedirectResponse(request.url_for("admin:list", identity=self.identity))'''


class PartyAdmin(ModelView, model=Party):
    column_list = [Party.id, Party.title, Party.quantity]


class PartyMemberAdmin(ModelView, model=PartyMember):
    column_list = [PartyMember.party,
                   PartyMember.member, PartyMember.member_status]


def init_admin(app, engine):
    admin = Admin(app, engine=engine,
                  authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(PartyAdmin)
    admin.add_view(PartyMemberAdmin)
