import _thread
from random import random
import time
import socket
from config import NUMBER_OF_PACKETS, WRAP_AROUND
from timer import Timer
import math
import tcp
from datetime import datetime
from socket import SHUT_RDWR


HOST = "localhost"  # The server's hostname or IP address
PORT = 50051  # The port used by the server

# Shared resources across threads
send_base = 0
mutex = _thread.allocate_lock()
send_timer = Timer(0.5)
N = 1 # window size
total_sent_packets = 0
total_retransmissions = {1:0,2:0,3:0,4:0}
retransmissions = {}

def set_window_size(num_packets):
    global send_base
    global N
    return min(N, num_packets - send_base)

def send(s):
    global mutex
    global send_base
    global send_timer
    global N
    global total_sent_packets
    global retransmissions

    print('Sending sequence number from 1 to ', NUMBER_OF_PACKETS)
    send_base = 0 
    next_seq_no = 0
    
    # Start the receiver thread
    _thread.start_new_thread(receive, (s,))

    congestion_flag = False;
    retransmissions = {}
    while send_base < NUMBER_OF_PACKETS:
        mutex.acquire()
        while next_seq_no < send_base + N:
            print('Sending packet with seq number ', next_seq_no)

            if next_seq_no in retransmissions:
                retransmissions[next_seq_no] += 1
            else:
                retransmissions[next_seq_no] = 1

            tcp.send(s, next_seq_no)
            total_sent_packets += 1
            next_seq_no += 1
        # Start the timer
        if not send_timer.running():
            print('Starting timer')
            send_timer.start()

        # Wait until a timer goes off or we get an ACK
        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            print('Sleeping')
            time.sleep(0.05)
            mutex.acquire()

        if send_timer.timeout():
            # Looks like we timed out
            print('Timeout')
            send_timer.stop()
            next_seq_no = send_base
            print("window size changed from ", N, "to ", math.ceil(N/2))
            N = math.ceil(N/2)
            congestion_flag = True
        else:
            print('Shifting window')
            if N < 10000:
                if not congestion_flag:
                    print("window size changed from ", N, "to ", N * 2, " at ", next_seq_no)
                    N *= 2
                else:
                    print("window size changed from ", N, "to ", N + 1, " at ", next_seq_no)
                    N += 1
            N = set_window_size(NUMBER_OF_PACKETS)
        mutex.release()

# Receive thread
def receive(s):
    global mutex
    global send_base
    global send_timer

    while True:
        ack_message = tcp.receive(s)
        #ack_message = s.recv(1024).decode('utf-8')
        print ("ack message received", ack_message)
        incoming_acks= [int(i) for i in ack_message.split(',')[:-1]]
        
        for ack in incoming_acks:
            # If we get an ACK for the first in-flight packet
            print('Got ACK', ack)
            wrapped_ack_base = int(send_base % WRAP_AROUND)
            if (ack >= wrapped_ack_base):
                mutex.acquire()
                send_base = send_base + 1
                print('Base updated', send_base)
                send_timer.stop()
                mutex.release()

def calculate_retransmissions():
    global total_retransmissions
    for i in retransmissions.keys():
        total_retransmissions[retransmissions[i]] += 1
    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    start = datetime.now()
    s.connect((HOST, PORT))
    s.send(b"network")
    data = s.recv(1024)
    if data.decode("utf-8") == "SUCCESS":
        print(f"Received SUCCESS. Sending data")
        send(s)
        print("total packets sent", total_sent_packets)
    s.shutdown(SHUT_RDWR)
    calculate_retransmissions()
    print("total retransmissions")
    print(total_retransmissions)
    end = datetime.now()
    print (end - start)
    s.close()




