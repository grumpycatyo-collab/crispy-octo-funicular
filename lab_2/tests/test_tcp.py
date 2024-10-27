import socket
import json
import time
import threading
import random


def send_command(command):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 9989))
        client.send(json.dumps(command).encode())
        response = client.recv(1024).decode()
        print("Response from server:", response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


def random_client_request():
    command_type = random.choice(["read", "write"])
    if command_type == "write":
        content = f"Random message {random.randint(1, 100)}"
        send_command({"type": "write", "content": content})
    else:
        send_command({"type": "read"})

threads = []
for _ in range(10):
    thread = threading.Thread(target=random_client_request)
    thread.start()
    threads.append(thread)
    time.sleep(random.uniform(0.1, 0.5))

for thread in threads:
    thread.join()
