import socket
import tcp
from config import WRAP_AROUND

HOST = ""  # Standard loopback interface address (localhost)
PORT = 50051  # Port to listen on (non-privileged ports are > 1023)
expected_num = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            list_of_received_messages = []
            received_message = conn.recv(1024).decode('utf-8')
            while (len(received_message) == 1024):
                list_of_received_messages.append(received_message)
                received_message = conn.recv(1024).decode('utf-8')
            list_of_received_messages.append(received_message)
            data = ''.join(list_of_received_messages)
            if not data:
                break
            if data == 'network':
                conn.sendall(b'SUCCESS')
            else:
                print("current sequence_no(s) received ", data)
                incoming_packets = [int(i) for i in data.split(',')[:-1]]
                
                for seq_num in incoming_packets:
                    
                    if (seq_num == expected_num):
                        print("Received correct ack")
                        print("Sending ack: "+ str(seq_num))
                        expected_num += 1
                        #tcp.send(conn, seq_num)
                        conn.send((str(seq_num) + ",").encode('utf-8'))
                    else:
                        print('Sending ACK', expected_num - 1, " as correct ack is not received")
                        #tcp.send(conn, expected_num - 1)
                        conn.sendall(str(expected_num - 1).encode('utf-8'))
                        break

                    if (expected_num >= WRAP_AROUND):
                        expected_num = 0
                