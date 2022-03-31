import socket
import threading
from config import NUMBER_OF_PACKETS
import time

HOST = "localhost"  # The server's hostname or IP address
PORT = 50051  # The port used by the server


def send_packets(packets):
    for packet in packets:
        s.send(str(packet).encode("utf-8"))


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
            thread = threading.Thread(target=send_packets, args=[sent_packets])
            thread.start()
            data = s.recv(1024).decode('utf-8')
            if not data:
                break
            print("Received: ", data)
            received_packets = [int(d) for d in data.split(",")]
            failed_packets = [x for x in sent_packets if x not in received_packets]
            if len(failed_packets) == 0:
                i += window_size
                window_size *= 2
            else:
                print("few packets failed:", failed_packets)
                window_size = 1        
        s.close()
print("finished")
