import socket

HOST = ""  # Standard loopback interface address (localhost)
PORT = 50051  # Port to listen on (non-privileged ports are > 1023)
expected_num = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            if data == 'network':
                conn.sendall(b'SUCCESS')
            else:
                print("current ack received ", data)
                incoming_packets = [int(i) for i in data.split(',')[:-1]]
                
                for seq_num in incoming_packets:
                    if (seq_num == expected_num):
                        print("Received correct acq")
                        print("Sending ack: "+ str(seq_num))
                        expected_num += 1
                        conn.send(str(str(seq_num) + ",").encode('utf-8'))
                    else:
                        print('Sending ACK', expected_num - 1, " as correct ack is not received")
                        conn.sendall(str(expected_num - 1).encode('utf-8'))
                        break
                