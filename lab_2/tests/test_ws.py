import asyncio
import websockets
import json


async def test_websocket_client():
    uri = "ws://127.0.0.1:8765"

    async with websockets.connect(uri) as websocket:
        response = await websocket.recv()
        print("Server:", json.loads(response)["message"])

        join_message = json.dumps({"type": "join_room", "room": "main"})
        await websocket.send(join_message)
        response = await websocket.recv()
        print("Server:", json.loads(response)["content"])

        send_message = json.dumps({"type": "send_msg", "content": "Hello, everyone!"})
        await websocket.send(send_message)
        response = await websocket.recv()
        print("Server:", json.loads(response)["content"])

        send_message = json.dumps({"type": "send_msg", "content": "Testing message broadcast."})
        await websocket.send(send_message)
        response = await websocket.recv()
        print("Server:", json.loads(response)["content"])

        leave_message = json.dumps({"type": "leave_room"})
        await websocket.send(leave_message)
        response = await websocket.recv()
        print("Server:", json.loads(response)["message"])


asyncio.get_event_loop().run_until_complete(test_websocket_client())
