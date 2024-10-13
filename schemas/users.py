from pydantic import BaseModel

class UserRequest(BaseModel):
    initData: str

class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str
    avatar: str

    points: int
    stars: int

class SearchUsersResponse(BaseModel):
    users: list[UserResponse]

class UserRefLink(BaseModel):
    link: str

class UserTwifBalance(BaseModel):
    twif: int