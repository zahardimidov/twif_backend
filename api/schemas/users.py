from typing import Optional, List, Dict, Any

from fastapi import Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone


class CreateUser(BaseModel):
    id: int
    username: str
    fullname: str

class InitDataRequest(BaseModel):
    initData: str = '{}'

class LeaderboardRequest(BaseModel):
    limit: Optional[int] = Field(Query(...))
    offset: Optional[str] = Field(Query(...))

class ConnectWalletRequest(InitDataRequest):
    address: str

class SetUserDailyBoost(InitDataRequest):
    boost_id: str


class UserCompleteTask(InitDataRequest):
    task_id: str

### RESPONSES ###

class UsersList(BaseModel):
    users: List[int]

class UserBoostsForNFT(BaseModel):
    boosts: Dict[str, float]

class AllDailyBoost(BaseModel):
    boosts: List['DailyBoost']

class DailyBoost(BaseModel):
    id: str
    stars: int
    multiplier: Optional[float] = Field(None)
    nolimit: Optional[bool] = Field(False)

class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str
    avatar: str

    points: float
    stars: int

class SaveGame(InitDataRequest):
    points: float

class SearchUsersResponse(BaseModel):
    users: list[UserResponse]

class UserTwifBalance(BaseModel):
    twif: int

class LeaderboardResponse(BaseModel):
    leaders: list[UserResponse]

class RefLinkResponse(BaseModel):
    link: str

class TaskResponse(BaseModel):
    id: str
    text: str
    url: str
    reward: int

class UserCompletedTasks(BaseModel):
    completed: List[Any]

class Tasks(BaseModel):
    tasks: List[TaskResponse]