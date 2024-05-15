import httpx
import asyncio
import time
import json
import logging
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)

guild_id = config["guild_id"]
token = config["token"]
webhook_url = config["webhook_url"]

headers = {
    'Authorization': token,
    'Content-Type': 'application/json',
}

def load_vanities():
    with open('vanities.txt', 'r') as file:
        return file.read().splitlines()

async def claim_vanity(vanity):
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(f'https://discord.com/invite/{vanity}')
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                twitter_creator_meta = soup.find('meta', attrs={'name': 'twitter:creator', 'content': '@discord'})

                if twitter_creator_meta:
                    logger.info(f'{vanity} is available')
                    await snipe_vanity(client, vanity)
                    break
                else:
                    logger.info(f'{vanity} is not available')
                await asyncio.sleep(1)
            except httpx.HTTPStatusError as e:
                logger.error(f'An HTTP error occurred: {e}')

async def snipe_vanity(client, vanity):
    start_time = time.time()
    while True:
        try:
            response = client.patch(f'https://discord.com/api/v10/guilds/{guild_id}/vanity-url',
                                          json={'code': vanity},
                                          headers=headers)
            response.raise_for_status()
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)
            logger.info(f'{vanity} sniped in {duration_ms} ms')
            await send_webhook(vanity, duration_ms)
            break
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = e.response.json().get('retry_after', 1)
                logger.warning(f'Rate limited. Retrying after {retry_after} seconds.')
                await asyncio.sleep(retry_after)
            else:
                logger.error(f'Failed to snipe {vanity}: {e}')
                break
