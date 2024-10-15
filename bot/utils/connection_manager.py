import asyncio
import signal
from functools import wraps
from bot.utils import logger

class ConnectionManager:
    def __init__(self):
        self.connections = set()

    def add(self, connection):
        self.connections.add(connection)

    def remove(self, connection):
        self.connections.discard(connection)

    async def close_all(self):
        for connection in self.connections:
            if hasattr(connection, 'close') and callable(connection.close):
                try:
                    await connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")

        closed_count = len(self.connections)
        self.connections.clear()


connection_manager = ConnectionManager()


def manage_connections(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()

        def signal_handler():
            asyncio.create_task(shutdown())

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        async def shutdown():
            await connection_manager.close_all()
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            [task.cancel() for task in tasks]
            await asyncio.gather(*tasks, return_exceptions=True)
            loop.stop()

        try:
            return await func(*args, **kwargs)
        finally:
            await connection_manager.close_all()

    return wrapper