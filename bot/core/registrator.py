import asyncio
import json
import os
from urllib.parse import urlparse
from pyrogram import Client
from bot.config import settings
from bot.utils import logger

PROXY_FILE_PATH = 'bot/config/proxies/session_proxy.json'

def parse_proxy_string(proxy_string):
    if not proxy_string:
        return None

    try:
        parsed = urlparse(proxy_string)
        scheme = parsed.scheme
        username = parsed.username
        password = parsed.password
        hostname = parsed.hostname
        port = parsed.port

        if not all([scheme, hostname, port]):
            raise ValueError("Invalid proxy string format")

        return {
            "scheme": scheme,
            "hostname": hostname,
            "port": port,
            "username": username,
            "password": password
        }
    except Exception as e:
        logger.error(f"Error parsing proxy string: {e}")
        return None


def get_proxy_input():
    proxy_string = input(
        'Enter proxy string (e.g., http://login:password@ip:port or socks5://login:password@ip:port) or press Enter to skip: ')
    return proxy_string, parse_proxy_string(proxy_string)


def save_session_proxy(session_name, proxy_string):
    try:
        if os.path.exists(PROXY_FILE_PATH):
            with open(PROXY_FILE_PATH, 'r') as f:
                proxies = json.load(f)
        else:
            proxies = {}

        proxies[session_name] = proxy_string

        with open(PROXY_FILE_PATH, 'w') as f:
            json.dump(proxies, f, indent=4)

        logger.success(f"Session '{session_name}' and its proxy have been saved to {PROXY_FILE_PATH}")
    except Exception as e:
        logger.error(f"Error saving session proxy: {e}")


async def register_sessions() -> None:
    try:
        API_ID = settings.API_ID
        API_HASH = settings.API_HASH

        if not API_ID or not API_HASH:
            raise ValueError("API_ID and API_HASH not found in the .env file.")

        while True:
            session_name = input('\nEnter the session name (press Enter to exit): ').strip()

            if not session_name:
                break

            proxy_string, proxy = get_proxy_input()

            async with Client(
                    name=session_name,
                    api_id=API_ID,
                    api_hash=API_HASH,
                    workdir="sessions/",
                    proxy=proxy
            ) as session:
                user_data = await session.get_me()

            logger.success(
                f'Session added successfully <ly>@{user_data.username}</ly> | {user_data.first_name} {user_data.last_name}')

            if proxy:
                logger.info(f"Proxy used: {proxy['scheme']}://{proxy['hostname']}:{proxy['port']}")

            if proxy_string:
                save_session_proxy(session_name, proxy_string)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(register_sessions())