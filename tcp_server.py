import socket
from config import WRAP_AROUND
from os.path import exists
import os
import threading

HOST = ""  
PORT = 50051  

#variable initialization for calculating throughput and graph
cur_seq_no = 0
dropped_seq_no = 0
cntr1 = 1
cntr2 = 1
seq_op = None
dseq_op = None

printFlag = False

#remove file if already exisits
def delete_file_if_already_exists(filename):
    file_exists = exists(filename)
    if file_exists:
        os.remove(filename)


# for creating graph: received sequnce number vs. time
def write_in_file_received():
    global cntr1
    global t1
    global seq_op
    t1 = threading.Timer(1, write_in_file_received)
    t1.start()
    seq_op.write(f"{cntr1} {cur_seq_no}\n")
	
    cntr1 += 1

# for creating graph: dropped sequence number vs. time
def write_in_file_dropped():
    global cntr2
    global t2
    global dseq_op
    t2 = threading.Timer(1, write_in_file_dropped)
    t2.start()
    dseq_op.write(f"{cntr2} {dropped_seq_no}\n")	
    cntr2 += 1

def main():
    
    global seq_op, dseq_op
    global cur_seq_no, dropped_seq_no

    dropped = 0
    expected_num = 0
    received = 0
    sum_goodput = 0
    count_goodput = 0
    total_packets_received = 0
    total_packets_dropped = 0
    

    # creating socket connection 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    
    # storing values in file to plot graphs
    delete_file_if_already_exists("seqno_time.txt")
    delete_file_if_already_exists("dropped_seqno_time.txt")
    seq_op = open("seqno_time.txt", "a")
    dseq_op = open("dropped_seqno_time.txt", "a")
    write_in_file_received()
    write_in_file_dropped()

    # accepting and printing connections
    conn, addr = s.accept()
    print(f"Receiver IP Address -> {HOST}:{PORT}")
    print(f"Sender IP Address -> {addr[0]}:{addr[1]}")

    while True:

        # receive messages from client
        list_of_received_messages = []
        received_message = conn.recv(1024).decode('utf-8')
        while (len(received_message) == 1024):
            list_of_received_messages.append(received_message)
            received_message = conn.recv(1024).decode('utf-8')
        list_of_received_messages.append(received_message)
        data = ''.join(list_of_received_messages)

        # exit if empty message received 
        if not data:
            break
        
        # handshake to make server client connection
        if data == 'network':
            conn.send(b'SUCCESS')
        else:

            # As python drops all packets to a stream, we are seperating our sequence numbers by ",". Generating sequence numbers from received message
            incoming_packets = [int(i) for i in data.split(',')[:-1]]
            
            for seq_num in incoming_packets:

                cur_seq_no = seq_num #populating graph2
                
                # correct sequence number received
                if (seq_num == expected_num):
                    if (printFlag): print("Received correct ack")
                    if (printFlag): print("Sending ack: "+ str(seq_num))
                    expected_num += 1
                    conn.send((str(seq_num) + ",").encode('utf-8'))
                    received += 1
                    total_packets_received += 1

                # incorrect sequence number received
                else:
                    if (printFlag): print('Sending ACK', expected_num - 1, " as correct ack is not received")
                    dropped += 1
                    total_packets_dropped += 1
                    dropped_seq_no = expected_num #populating graph3
                    # conn.send(str(expected_num - 1).encode('utf-8'))
    
                # wrapping around the sequence number
                if (expected_num >= WRAP_AROUND):
                    expected_num = 0

                # calculating good put
                if received == 1000:
                    sum_goodput += 1000/(1000+dropped)
                    count_goodput += 1
                    received = 0
                    dropped = 0

    print("Average good put is -> ", sum_goodput / count_goodput)
    print(f"Number of packets received: {total_packets_received} and number of packets sent: {total_packets_dropped + total_packets_received}")

    t1.cancel()
    t2.cancel()

if __name__ == "__main__":
    main()
