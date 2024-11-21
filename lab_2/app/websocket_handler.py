import asyncio
import websockets
import json
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer


class ChatRoom:
    def __init__(self):
        self.clients = set()

    async def broadcast(self, message):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])


class WebSocketServer:
    def __init__(self):
        self.rooms = {"main": ChatRoom()}

    async def handler(self, websocket, path):
        current_room = None

        try:
            await websocket.send(json.dumps({"type": "connect", "message": "Connected to WebSocket chat server"}))

            async for message in websocket:
                data = json.loads(message)
                command = data.get("type")

                if command == "join_room":
                    room_name = data["room"]
                    if current_room:
                        current_room.clients.remove(websocket)
                    current_room = self.rooms.setdefault(room_name, ChatRoom())
                    current_room.clients.add(websocket)
                    await current_room.broadcast(json.dumps({"type": "message", "content": f"User joined {room_name}"}))

                elif command == "send_msg" and current_room:
                    await current_room.broadcast(json.dumps({
                        "type": "message",
                        "content": data["content"]
                    }))

                elif command == "leave_room" and current_room:
                    current_room.clients.remove(websocket)
                    await current_room.broadcast(json.dumps({"type": "message", "content": "User left the room"}))
                    current_room = None
                    await websocket.send(json.dumps({"type": "leave", "message": "You left the room"}))

        finally:
            if current_room:
                current_room.clients.remove(websocket)

    def run(self):
        server = websockets.serve(self.handler, "0.0.0.0", 8765)
        print("WebSocket server started on port 8765")
        asyncio.get_event_loop().run_until_complete(server)
        print("WebSocket server listening for connections...")
        asyncio.get_event_loop().run_forever()


class HTTPHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'app/index.html'
        return super().do_GET()


def start_http_server():
    http_server = HTTPServer(('0.0.0.0', 8081), HTTPHandler)
    print("HTTP server started on port 8081")
    http_server.serve_forever()


def start_websocket_server():
    websocket_app = WebSocketServer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_app.run())
    loop.run_forever()


