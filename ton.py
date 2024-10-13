
import json
from aiohttp import ClientSession
import asyncio
import asyncio
import json
import ssl

import certifi
from utils import cache_decorator


sslcontext = ssl.create_default_context(cafile=certifi.where())

COLLECTION_ID = 'EQCJB8LHXRAmdcecufPbzvOMj2C95hWvtSKE5iiDs3-qU8wP'
TWIF_ID = 'EQDV3cbziPHz8wEcDYt-9iDOomlc3bFZQSx0WiZFCv7fh7oX'

def filterCollection(data):
    res = []
    for el in data:
        if not el.get('sale'):
            continue

        value = int(el['sale']['price']['value']) / 1_000_000_000
        if value == 0:
            continue

        element = dict(
            address=el['address'],
            collection = el['collection'],

            name = el['metadata']['name'],
            description = el['metadata']['description'],
            image = el['metadata']['image'],

            color = next([attribute['value'] for attribute in el['metadata']['attributes'] if 'color' in attribute['trait_type']]),
            number = next([attribute['value'] for attribute in el['metadata']['attributes'] if 'Number' in attribute['trait_type']]),

            sale = {
                'token_name': el['sale']['price']['token_name'],
                'value': value
            },
            previews = el['previews']
        )
        res.append(element)
    return sorted(res, key=lambda obj: -obj['sale']['value'])


@cache_decorator
async def get_nft_collection():
    async with ClientSession() as session:
        response = await session.get(f'https://tonapi.io/v2/nfts/collections/{collection_id}/items', ssl=sslcontext)
        data = await response.json()

    return filterCollection(data['nft_items'])


@cache_decorator
async def get_account_nft(account_id = 'EQA0OW2trwp66mB6KxZygH_rTY65jbvNv0580py5WOkXwfVu'):
    async with ClientSession() as session:
        response = await session.get(f'https://tonapi.io/v2/accounts/{account_id}/nfts?collection={COLLECTION_ID}', ssl=sslcontext)
        data = await response.json()
        
    with open('account_nft.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


@cache_decorator
async def get_twif_balance(account_id='EQA0OW2trwp66mB6KxZygH_rTY65jbvNv0580py5WOkXwfVu'):
    async with ClientSession() as session:
        response = await session.get(f'https://tonapi.io/v2/accounts/{account_id}/jettons/{TWIF_ID}', ssl=sslcontext)
        data = await response.json()

        if isinstance(data, dict) and data.get('balance'):
            return int(data['balance']) / 1_000_000_000
    return 0


if __name__ == '__main__':
    asyncio.run(get_twif_balance())
