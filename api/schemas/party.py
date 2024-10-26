from pydantic import BaseModel, Field, computed_field
from api.schemas.users import InitDataRequest
from typing import Optional, List
from config import WEBHOOK_HOST



class PartyCreate(InitDataRequest):
    title: str = 'Great Again'
    quantity: int = 50

    founder_share: float = 0.3
    members_share: float = 0.4
    project_share: float = 0.2
    voters_share: float = 0.1

    chat_url: Optional[str] = Field(None, description="Telegram Chat URL")

    nft_requirement: Optional[str] = Field(None, description="NFT color [white, silver or black]")
    twif_requirement: Optional[int] =  Field(None, description="Amount of twif")


class PartyUpdate(PartyCreate):
    description: str = ''
    party_id: str

class SquadCreate(PartyCreate):
    founder_ids: list[int]

class JoinPartyRequest(InitDataRequest):
    party_id: str

class VotePartyRequest(InitDataRequest):
    party_id: str


### RESPONSES

class PartyPoints(BaseModel):
    points: int

class PartyResponse(BaseModel):
    id: str

    title: str
    description: Optional[str] = Field('', description="Party description")
    logo: str

    chat_url: Optional[str] = Field(None, description="Telegram Chat URL")
    level: int

    @computed_field
    def logoURL(self) -> str:
        return WEBHOOK_HOST + f"/media/logos/{self.logo.split('/')[-1]}"


class PartyLeaderResponse(BaseModel):
    id: str

    title: str
    logoURL: str
    
    points: int
    quantity: int

class PartyInviteResponse(BaseModel):
    id: str

    title: str
    logoURL: str

class PartyLeaderboardResponse(BaseModel):
    leaders: list[PartyLeaderResponse]

class PartyInvites(BaseModel):
    invites: List[PartyInviteResponse]

class PartyMemberResponse(BaseModel):
    party_id: str
    user_id: int
    status: str
    username: str
    fullname: str
    avatar: str

class PartyMembersResponse(BaseModel):
    members: List[PartyMemberResponse]