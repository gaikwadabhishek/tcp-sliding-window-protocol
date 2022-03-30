import socket

HOST = ""  # Standard loopback interface address (localhost)
PORT = 50051  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024).decode('utf=8')
            # import pdb; pdb.set_trace()
            if not data:
                break
            if data == 'network':
                conn.sendall(b'SUCCESS')
            else:
                conn.sendall(data.encode('utf-8'))