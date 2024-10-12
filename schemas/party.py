from pydantic import BaseModel

class PartyResponse(BaseModel):
    title: int
    quantity: int
    logo: str

class PartyCreate(BaseModel):
    title: str 
    quantity: int

    founder_share: float
    members_share: float
    project_share: float
    voters_share: float

class JoinPartyRequest(BaseModel):
    party_id: str
