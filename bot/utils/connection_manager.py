from functools import wraps

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
                    # Используем print вместо logger
                    print(f"Error closing connection: {e}")

        closed_count = len(self.connections)
        self.connections.clear()

connection_manager = ConnectionManager()

def manage_connections(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        finally:
            await connection_manager.close_all()

    return wrapper
