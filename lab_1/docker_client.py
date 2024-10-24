import socket
import base64


def send_authenticated_request(data, content_type):
    username = "408"
    password = "204"

    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 8000))
    request = f"""POST /upload HTTP/1.1
Host: localhost:8000
Authorization: Basic {credentials}
Content-Type: {content_type}
Content-Length: {len(data)}

{data}"""

    s.send(request.encode())
    response = s.recv(4096).decode()
    s.close()
    return response