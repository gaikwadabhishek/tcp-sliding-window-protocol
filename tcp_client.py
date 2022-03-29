import socket
from config import num_packets

HOST = "localhost"  # The server's hostname or IP address
PORT = 4322  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"network")
    data = s.recv(1024)
    if data.decode("utf-8") == "SUCCESS":
        print(f"Received SUCCESS. Sending data")
        for i in range(num_packets):
            s.sendall(str(i).encode('utf-8'))
            data = s.recv(1024).decode('utf-8')
            if not data:
                break
            if int(data) == i:
                print("Found correct ack")
                continue
            else:
                print("Missing some acks, exiting")
                break

print("finished")
