from typing import List, Dict

from starlette.websockets import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connections_per_path: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, path: str):
        await websocket.accept()
        if path not in self.active_connections:
            print('path', path)
            self.active_connections[path] = []
            self.connections_per_path[path] = 0
        self.active_connections[path].append(websocket)
        self.connections_per_path[path] += 1

        # Print information about the new connection
        print('New connection:', websocket.client, 'to path:', path)

        # Print total number of connections
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        print('Total connections:', total_connections)

        # Print connections per path
        print('Connections per path:', self.connections_per_path)

    def disconnect(self, websocket: WebSocket, path: str):
        if path in self.active_connections:
            try:
                self.active_connections[path].remove(websocket)
                self.connections_per_path[path] -= 1
            except ValueError:
                pass  # WebSocket object not found in the list, so ignore the error

    async def broadcast(self, data: str, path: str):
        if path in self.active_connections:
            for connection in self.active_connections[path]:
                await connection.send_text(data)

