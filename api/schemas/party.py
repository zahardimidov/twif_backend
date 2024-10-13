from pydantic import BaseModel
from api.schemas.users import InitDataRequest


class PartyCreate(InitDataRequest):
    title: str = 'Great Again'
    quantity: int = 50

    founder_share: float = 0.3
    members_share: float = 0.4
    project_share: float = 0.2
    voters_share: float = 0.1

class SquadCreate(InitDataRequest):
    title: str = 'Republican Party'
    quantity: int = 100

    founder_ids: list[int]

    founder_share: float
    members_share: float
    project_share: float
    voters_share: float

class JoinPartyRequest(InitDataRequest):
    party_id: str

class VotePartyRequest(InitDataRequest):
    party_id: str


### RESPONSES

class PartyResponse(BaseModel):
    title: int
    quantity: int
    logo: str