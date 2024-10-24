import asyncio
import websockets
import json


class ChatRoom:
    def __init__(self):
        self.clients = set()
        self.messages = []

    async def broadcast(self, message):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])


class WebSocketServer:
    def __init__(self):
        self.rooms = {"main": ChatRoom()}

    async def handler(self, websocket, path):
        room = self.rooms["main"]
        room.clients.add(websocket)
        try:
            await websocket.send(json.dumps({"type": "connect", "message": "Connected to chat room"}))

            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "message":
                    await room.broadcast(json.dumps({
                        "type": "message",
                        "content": data["content"]
                    }))
        finally:
            room.clients.remove(websocket)

    def run(self):
        server = websockets.serve(self.handler, "0.0.0.0", 8765)
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()


websocket_app = WebSocketServer()