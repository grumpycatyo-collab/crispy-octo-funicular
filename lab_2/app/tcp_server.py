import socket
import threading
import time
import random
import json
from threading import Lock

file_lock = Lock()
write_count = 0
write_lock = Lock()
read_lock = Lock()


def handle_client(client_socket, addr):
    print(f"Client connected from {addr}")
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            command = json.loads(data)

            if command["type"] == "write":
                time.sleep(random.randint(1, 7))
                with write_lock:
                    global write_count
                    write_count += 1
                    if write_count == 1:
                        read_lock.acquire()

                with file_lock:
                    with open("data.txt", "a") as f:
                        f.write(f"{command['content']}\n")

                with write_lock:
                    write_count -= 1
                    if write_count == 0:
                        read_lock.release()

                client_socket.send("Write successful".encode())
                print(f"Write operation successful for client {addr}")

            elif command["type"] == "read":
                time.sleep(random.randint(1, 7))
                with read_lock:
                    with file_lock:
                        with open("data.txt", "r") as f:
                            content = f.read()
                            client_socket.send(content.encode())
                print(f"Read operation successful for client {addr}")

        except Exception as e:
            print(f"Error for client {addr}: {e}")
            break

    print(f"Client {addr} disconnected")
    client_socket.close()


def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9989))
    print("Server started on port 9989")
    server.listen(5)
    print("Server listening for connections...")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()
