from fastapi import Query
from pydantic import BaseModel, Field
from .users import UserResponse
from typing import Optional

class LeaderboardRequest(BaseModel):
    limit: Optional[int] = Field(Query(...))
    offset: Optional[str] = Field(Query(...))

class LeaderboardResponse(BaseModel):
    leaders: list[UserResponse]