from fastapi import APIRouter
from api.schemas import *
from ton_requests import get_nft_collection, groupCollection, getCollectionColors

router = APIRouter(prefix='/nft', tags=['NFT'])


@router.get('/collection', response_model=NFTCollectionItems)
async def get_nft_items():
    nft = await get_nft_collection()

    return NFTCollectionItems(items=nft)

@router.get('/collection/groups', response_model=NFTCollectionGroups)
async def get_nft_groups():
    nft = await get_nft_collection()
    groups = groupCollection(nft)

    return NFTCollectionGroups(groups=groups)

@router.get('/collection/colors', response_model=NFTCollectionColors)
async def get_nft_colors():
    nft = await get_nft_collection()
    colors = getCollectionColors(nft)

    return NFTCollectionColors(colors=colors)
