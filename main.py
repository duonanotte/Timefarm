import asyncio
import sys
import os
import signal

from bot.utils.banner import banner
from bot.utils.logger import logger
from bot.utils.launcher import process
from bot.utils.connection_manager import connection_manager

def suppress_errors():
    sys.stderr = open(os.devnull, 'w')

async def main():
    try:
        await process()
    except asyncio.CancelledError:
        pass
    finally:
        await connection_manager.close_all()

def signal_handler(signum, frame):
    sys.exit(0)


if __name__ == '__main__':
    banner()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    finally:
        logger.info("<lr>Bot stopped by user</lr>")
        suppress_errors()
