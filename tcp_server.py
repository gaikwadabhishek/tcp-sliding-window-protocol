# CODE SUBMITTED BY AMEYA M. AND ABHISHEK G.

# imports
import socket
from os.path import exists
import os
import threading

# CONFIG VARIABLES:
WRAP_AROUND = 65536
HOST = ""  #IP ADDRESS OF SERVER
PORT = 50051  
printFlag = False

#variable initialization for calculating throughput and graph
cur_seq_no = 0
dropped_seq_no = 0
counter1 = 1
counter2 = 1
seq_op = None
dseq_op = None

#remove file if already exisits
def delete_file_if_already_exists(filename):
    if exists(filename): os.remove(filename)
        
# for creating graph: received sequnce number vs. time
def write_in_file_received():
    global counter1, t1, seq_op
    t1 = threading.Timer(1, write_in_file_received)
    t1.start()
    seq_op.write(f"{counter1} {cur_seq_no}\n")
    counter1 += 1

# for creating graph: dropped sequence number vs. time
def write_in_file_dropped():
    global counter2, t2, dseq_op
    t2 = threading.Timer(1, write_in_file_dropped)
    t2.start()
    dseq_op.write(f"{counter2} {dropped_seq_no}\n")	
    counter2 += 1

# receive function using python sockets(tcp)
def tcp_receive(conn):
    list_of_received_messages = []
    received_message = conn.recv(1024).decode('utf-8')
    while len(received_message) == 1024:
        list_of_received_messages.append(received_message)
        received_message = conn.recv(1024).decode('utf-8')
    list_of_received_messages.append(received_message)
    return ''.join(list_of_received_messages)

def main():

    # declaring local variables and counters
    global seq_op, dseq_op, cur_seq_no, dropped_seq_no
    sent_packets = 0
    expected_num = 0
    received = 0
    sum_goodput = 0
    count_goodput = 0
    total_packets_received = 0
    total_packets_sent = 0

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

    # print(f"Receiver IP Address \t->\t {HOST}:{PORT}")
    print(f"Receiver IP Address \t->\t 10.0.0.218:50051")
    # print(f"Sender IP Address \t->\t {addr[0]}:{addr[1]}")
    print(f"Sender IP Address \t->\t 10.0.0.197:50051")

    while True:

        # receive messages from client
        data = tcp_receive(conn)
        
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
                sent_packets += 1
                total_packets_sent += 1
                
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
                    if (printFlag): print("correct ack is not recevied ->", seq_num)
                    if seq_num - 1 == expected_num:
                        dropped_seq_no = expected_num
                    
                # wrapping around the sequence number
                if (expected_num >= WRAP_AROUND):
                    expected_num = 0

                # calculating good put
                if received == 1000:
                    sum_goodput += 1000/(sent_packets)
                    count_goodput += 1
                    received = 0
                    sent_packets = 0

    print("Average Good Put\t->\t", sum_goodput / count_goodput)
    print("Packets Received\t->\t", total_packets_received)
    print("Packets Sent\t\t->\t", total_packets_sent)
    t1.cancel()
    t2.cancel()

if __name__ == "__main__":
    main()