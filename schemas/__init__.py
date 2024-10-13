from fastapi import Request
from schemas.leaders import *
from schemas.party import *
from schemas.users import *
from schemas.nft import *


class WebAppRequest(Request):
    def __init__(self, webapp_user, **kwargs):
        self.__dict__.update(kwargs)
        self.webapp_user: UserResponse = webapp_user
