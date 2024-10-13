from fastapi import APIRouter
from schemas import *
from ton import get_nft_collection

router = APIRouter(prefix='/nft', tags=['NFT'])


@router.get('/collection', response_model=NFTCollectionItems)
async def get_nft_items():
    nft = await get_nft_collection()

    return NFTCollectionItems(items=nft)
