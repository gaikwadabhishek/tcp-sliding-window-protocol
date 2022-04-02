import socket
from time import sleep, time

HOST = ""  # Standard loopback interface address (localhost)
PORT = 50051  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024).decode('utf=8')
            print(data)
            sleep(10)
            if not data:
                break
            if data == 'network':
                conn.send(b'SUCCESS')
            else:
                conn.send(data.encode('utf-8'))