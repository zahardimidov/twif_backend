from api.schemas.users import InitDataRequest
from typing import Any, List
from pydantic import BaseModel

class SendTransaction(InitDataRequest):
    boc: str

class StarsTransaction(SendTransaction):
    offer_id: str

class StarsOffer(BaseModel):
    amount: int
    ton: float

class StarsOffers(BaseModel):
    offers: List[StarsOffer]