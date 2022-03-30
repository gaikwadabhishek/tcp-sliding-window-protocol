import socket
from config import NUMBER_OF_PACKETS
import time

HOST = "localhost"  # The server's hostname or IP address
PORT = 50051  # The port used by the server

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
            s.sendall(",".join(str(x) for x in sent_packets).encode("utf-8"))
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
            
            #time.sleep(5)    
        s.close()

        # for i in range(NUMBER_OF_PACKETS):
        #     s.sendall(str(i).encode('utf-8'))
        #     data = s.recv(1024).decode('utf-8')
        #     if not data:
        #         break
        #     if int(data) == i:
        #         print("Found correct ack")
        #         continue
        #     else:
        #         print("Missing some acks, exiting")
        #         break

print("finished")
