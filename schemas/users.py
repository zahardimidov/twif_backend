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

class NFT(BaseModel):
    id: int
    title: str

class UserBalance(BaseModel):
    twif: int
    nfts: list[NFT]