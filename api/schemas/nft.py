from pydantic import BaseModel
from typing import List, Dict


class NFTPreview(BaseModel):
    resolution: str
    url: str

class NFTSale(BaseModel):
    token_name: str
    value: float

class NFTCollection(BaseModel):
    address: str
    name: str
    description: str

class NFT(BaseModel):
    address: str
    collection: NFTCollection

    name: str
    description: str
    image: str
    
    color: str
    number: int

    sale: NFTSale
    previews: List[NFTPreview]

class NFTCollectionItems(BaseModel):
    items: List[NFT]

class NFTCollectionGroups(BaseModel):
    groups: Dict[str, List[NFT]]

class NFTCollectionColors(BaseModel):
    colors: List[str]