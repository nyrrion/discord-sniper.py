import aiohttp
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

async def check_token_validity():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://discord.com/api/v10/users/@me', headers=headers) as response:
            if response.status == 200:
                logger.info('Token is valid')
                return True
            else:
                logger.error('Token is invalid')
                return False

async def claim_vanity(vanity):
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(f'https://discord.com/invite/{vanity}') as response:
                    response.raise_for_status()
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    twitter_creator_meta = soup.find('meta', attrs={'name': 'twitter:creator', 'content': '@discord'})

                    if twitter_creator_meta:
                        logger.info(f'{vanity} is available')
                        await snipe_vanity(session, vanity)
                        break
                    else:
                        logger.info(f'{vanity} is not available')
                    await asyncio.sleep(1)
            except aiohttp.ClientResponseError as e:
                logger.error(f'An HTTP error occurred: {e}')

async def snipe_vanity(session, vanity):
    start_time = time.time()
    while True:
        try:
            async with session.patch(f'https://discord.com/api/v10/guilds/{guild_id}/vanity-url',
                                     json={'code': vanity},
                                     headers=headers) as response:
                response.raise_for_status()
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                logger.info(f'{vanity} sniped in {duration_ms} ms')
                await send_webhook(vanity, duration_ms)
                break
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                retry_after = (await response.json()).get('retry_after', 1)
                logger.warning(f'Rate limited. Retrying after {retry_after} seconds.')
                await asyncio.sleep(retry_after)
            else:
                logger.error(f'Failed to snipe {vanity}: {e}')
                break

async def send_webhook(vanity, duration_ms):
    async with aiohttp.ClientSession() as session:
        payload = {
            'content': f'Successfully sniped {vanity} in {duration_ms} ms'
        }
        async with session.post(webhook_url, json=payload) as response:
            response.raise_for_status()
            logger.info('Webhook sent successfully')

async def main():
    if not await check_token_validity():
        return

    vanities = load_vanities()
    tasks = [claim_vanity(vanity) for vanity in vanities]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

