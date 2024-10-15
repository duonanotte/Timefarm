import asyncio
import sys

from bot.utils.banner import banner
from bot.utils import logger
from bot.utils.launcher import process
from bot.utils.connection_manager import manage_connections

@manage_connections
async def main():
    await process()


if __name__ == '__main__':
    banner()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("<lr>Bot stopped by user.</lr>")
        sys.exit(0)