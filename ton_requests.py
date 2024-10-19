
import json
from aiohttp import ClientSession
import asyncio
import asyncio
import json
import ssl

import certifi
from utils import cache_decorator

from ton.utils import Cell as cell
import base64
from tonsdk.boc._cell import Cell


sslcontext = ssl.create_default_context(cafile=certifi.where())

COLLECTION_ID = 'EQCJB8LHXRAmdcecufPbzvOMj2C95hWvtSKE5iiDs3-qU8wP'
TWIF_ID = 'EQDV3cbziPHz8wEcDYt-9iDOomlc3bFZQSx0WiZFCv7fh7oX'

def filterCollection(data, sale = True):
    res = []
    for el in data:
        if sale and not el.get('sale'):
            continue

        element = dict(
            address=el['address'],
            collection = el['collection'],

            name = el['metadata']['name'],
            description = el['metadata']['description'],
            image = el['metadata']['image'],

            color = next(iter([attribute['value'] for attribute in el['metadata']['attributes'] if 'color' in attribute['trait_type']])),
            number = next(iter([attribute['value'] for attribute in el['metadata']['attributes'] if 'Number' in attribute['trait_type']])),

            previews = el['previews']
        )

        if sale:
            value = int(el['sale']['price']['value']) / 1_000_000_000
            if value == 0:
                continue

            element.update(sale = {
                'token_name': el['sale']['price']['token_name'],
                'value': value
            })
        res.append(element)
    return sorted(res, key=lambda obj: obj['color'])


def groupCollection(data):
    response = {}
    for i in data:
        if not i['color'] in response:
            response[i['color']] = []
        response[i['color']].append(i)
    return response

def getCollectionColors(data):
    return set([i['color'] for i in data])


@cache_decorator
async def get_nft_collection():
    async with ClientSession() as session:
        response = await session.get(f'https://tonapi.io/v2/nfts/collections/{COLLECTION_ID}/items', ssl=sslcontext)
        data = await response.json()

    return filterCollection(data['nft_items'])


@cache_decorator
async def get_account_nft(account_id = 'EQA0OW2trwp66mB6KxZygH_rTY65jbvNv0580py5WOkXwfVu'):
    async with ClientSession() as session:
        response = await session.get(f'https://tonapi.io/v2/accounts/{account_id}/nfts?collection={COLLECTION_ID}', ssl=sslcontext)
        data = await response.json()
        
    with open('account_nft.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(filterCollection(data['nft_items'], sale=False), indent=4, ensure_ascii=False))


    return filterCollection(data['nft_items'], sale=False)


@cache_decorator
async def get_twif_balance(account_id='EQA0OW2trwp66mB6KxZygH_rTY65jbvNv0580py5WOkXwfVu'):
    async with ClientSession() as session:
        response = await session.get(f'https://tonapi.io/v2/accounts/{account_id}/jettons/{TWIF_ID}', ssl=sslcontext)
        data = await response.json()

        if isinstance(data, dict) and data.get('balance'):
            return int(data['balance']) / 1_000_000_000
    return 0

async def getTransactions(address, limit = 5, hash = None):
    url = f'https://tonapi.io/v2/getTransactions?address={address}&limit={limit}&to_lt=0&archival=false'
    async with ClientSession() as session:
        if hash:
            url += f'?hash={hash}'
        response = await session.get(url, ssl=sslcontext)
        data = await response.json()
    return data



async def getLastByBoc(address, boc):
    msg_body = base64.b64decode(boc)
    cell_data: Cell = cell.one_from_boc(msg_body)
    hash_hex = cell_data.bytes_hash().hex()

    res = await getTransactions(address=address, limit=1, hash=hash_hex)

    return 'ok' in res


if __name__ == '__main__':
    asyncio.run(get_account_nft())
