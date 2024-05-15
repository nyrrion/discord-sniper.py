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
    'Authorization': f'{token}',
    'Content-Type': 'application/json',
}

def load_vanities():
    with open('vanities.txt', 'r') as file:
        return file.read().splitlines()

async def claim_vanity(vanity):
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        while True:
            try:
                async with session.get(f'https://discord.com/invite/{vanity}') as response:
                    response.raise_for_status()
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    og_description = soup.find('meta', property='og:description')

                    if og_description and og_description['content'] == 'Discord is the easiest way to communicate over voice, video, and text. Chat, hang out, and stay close with your friends and communities.':
                        logger.info(f'{vanity} is available')
                        await snipe_vanity(session, vanity, start_time)
                        break
                    else:
                        logger.info(f'{vanity} is not available')
                    await asyncio.sleep(1)
            except aiohttp.ClientResponseError as e:
                logger.error(f'An HTTP error occurred: {e}')

async def snipe_vanity(session, vanity, start_time):
    while True:
        async with session.patch(f'https://discord.com/api/v10/guilds/{guild_id}/vanity-url',
                                 json={'code': vanity},
                                 headers=headers) as response:
            if response.status in [200, 201]:
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                logger.info(f'{vanity} sniped in {duration_ms} ms')
                await send_webhook(session, vanity, duration_ms)
                break
            elif response.status == 429:
                retry_after = (await response.json()).get('retry_after', 1)
                logger.warning(f'Rate limited. Retrying after {retry_after} seconds.')
                await asyncio.sleep(retry_after)
            else:
                logger.info(f'/{vanity} is being sniped')
                await asyncio.sleep(1)

async def send_webhook(session, vanity, duration_ms):
    data = {
        'content': 'Sniping finished',
        'embeds': [{
            'description': f'{vanity} has been sniped for this server in {duration_ms} ms'
        }]
    }
    async with session.post(webhook_url, json=data, headers={'Content-Type': 'application/json'}) as response:
        if response.status in [200, 204]:
            logger.info('Webhook sent successfully.')
        else:
            logger.error('Failed to send webhook.')

async def main():
    vanities = load_vanities()
    tasks = [claim_vanity(vanity) for vanity in vanities]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
