import socket

HOST = "172.20.10.3"  # The server's hostname or IP address
PORT = 4322  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"network")
    data = s.recv(1024)
    if data.decode("utf-8") == "SUCCESS":
        for i in range(100):
            data = s.recv(1024)

print(f"Received {data!r}")