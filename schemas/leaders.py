from pydantic import BaseModel
from .users import UserResponse

class LeaderboardRequest(BaseModel):
    limit: int = 20
    offset: int = 0

class LeaderboardResponse(BaseModel):
    leaders: list[UserResponse]