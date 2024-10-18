from fastapi import Request
from api.schemas.party import *
from api.schemas.users import *
from api.schemas.nft import *
from api.schemas.transaction import *


class WebAppRequest(Request):
    def __init__(self, webapp_user, **kwargs):
        self.__dict__.update(kwargs)
        self.webapp_user: UserResponse = webapp_user
