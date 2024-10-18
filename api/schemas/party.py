from pydantic import BaseModel, Field
from api.schemas.users import InitDataRequest
from typing import Optional



class PartyCreate(InitDataRequest):
    title: str = 'Great Again'
    quantity: int = 50

    founder_share: float = 0.3
    members_share: float = 0.4
    project_share: float = 0.2
    voters_share: float = 0.1

    nft_requirement: Optional[str] = Field(None, description="NFT color [white, silver or black]")
    twif_requirement: Optional[int] =  Field(None, description="Amount of twif")

class SquadCreate(PartyCreate):
    founder_ids: list[int]

class JoinPartyRequest(InitDataRequest):
    party_id: str

class VotePartyRequest(InitDataRequest):
    party_id: str


### RESPONSES

class PartyResponse(BaseModel):
    title: int
    quantity: int
    logo: str