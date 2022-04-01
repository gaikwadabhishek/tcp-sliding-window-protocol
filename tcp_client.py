import socket
import threading
from config import NUMBER_OF_PACKETS
import time

HOST = "localhost"  # The server's hostname or IP address
PORT = 50051  # The port used by the server


resume_process = threading.Event()
acks_recvd = True


def send_packets(s, packets):
    for packet in packets:
        s.send(str(packet).encode("utf-8"))


def receive_packets(s, packets):
    global acks_recvd
    while True:
        packets = set(packets)
        data = int(s.recv(1024).decode('utf-8'))
        packets.discard(data)
        if not packets:
            acks_recvd = True
            resume_process.set()
            return


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"network")
    data = s.recv(1024)
    if data.decode("utf-8") == "SUCCESS":
        print(f"Received SUCCESS. Sending data")
        i = 1
        window_size = 1
        while i <= NUMBER_OF_PACKETS:
            if i + window_size > NUMBER_OF_PACKETS:
                window_size = NUMBER_OF_PACKETS - i + 1
            sent_packets = list(range(i, i + window_size))
            print("Sending packets: ", sent_packets)
            acks_recvd = False
            thread = threading.Thread(target=send_packets, args=[s, sent_packets])
            thread.start()
            receive_packets(s, sent_packets)
            resume_process.wait(timeout=10)
            if acks_recvd:
                i += window_size
                window_size *= 2 
            else:
                window_size = 1    
        s.close()
print("finished")
