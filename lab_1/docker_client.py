import socket


def send_to_docker_server(data, content_type):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 8000))

    request = f"""POST /upload HTTP/1.1
Host: localhost:8000
Content-Type: {content_type}
Content-Length: {len(data)}

{data}"""

    s.send(request.encode())
    response = s.recv(4096).decode()
    s.close()
    return response