from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field


class InitDataRequest(BaseModel):
    initData: str = '{}'

class LeaderboardRequest(BaseModel):
    limit: Optional[int] = Field(Query(...))
    offset: Optional[str] = Field(Query(...))


### RESPONSES ###

class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str
    avatar: str

    points: int
    stars: int

class SearchUsersResponse(BaseModel):
    users: list[UserResponse]

class UserTwifBalance(BaseModel):
    twif: int

class LeaderboardResponse(BaseModel):
    leaders: list[UserResponse]

class RefLinkResponse(BaseModel):
    link: str
