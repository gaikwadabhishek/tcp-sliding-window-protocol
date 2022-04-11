# CODE SUBMITTED BY AMEYA M. AND ABHISHEK G.

# imports
import _thread
import threading
import time
import socket
import math
from socket import SHUT_RDWR
from datetime import datetime
from tcp_server import delete_file_if_already_exists
import random
from collections import defaultdict

#CONFIGS
NUMBER_OF_PACKETS = 10000000
#drop probabilty in percent
DROP_PROBABILITY = 1
WRAP_AROUND = 65536
# IP Addr of Server
HOST = "localhost"  # The server's hostname or IP address
PORT = 50051  # The port used by the server

# Timer class to handle start, stop and handle timeouts 
class Timer(object):
    TIMER_STOP = -1

    def __init__(self, duration):
        self._start_time = self.TIMER_STOP
        self._duration = duration

    # Starts the timer
    def start(self):
        if self._start_time == self.TIMER_STOP:
            self._start_time = time.time()

    # Stops the timer
    def stop(self):
        if self._start_time != self.TIMER_STOP:
            self._start_time = self.TIMER_STOP

    # Determines whether the timer is runnning
    def running(self):
        return self._start_time != self.TIMER_STOP

    # Determines whether the timer timed out
    def timeout(self):
        if not self.running():
            return False
        else:
            return time.time() - self._start_time >= self._duration


# variables to populate graph data
counter = 1
win_op = None

# Shared resources across threads
send_base = 0
mutex = _thread.allocate_lock()
send_timer = Timer(0.01)
N = 1 # window size
total_sent_packets = 0
retransmissions = {}
printFlag = False
sent_packets = set()

def write_in_file():
    global counter, t, win_op
    t = threading.Timer(1, write_in_file)
    t.start()
    win_op.write(f"{counter} {N}\n")
    counter += 1


# sending pakcets using socket connection and probablistically dropping packets
def socket_send(s, next_seq_no):
    next_seq_no = int(next_seq_no % WRAP_AROUND)
    s.send((str(next_seq_no) + ",").encode('utf-8'))


# receiving packets
# as we are using python socket streaming, we need to seperate messages using ",". Logic to extract sequence numbers from received messages
def socket_receive(s):
    list_of_received_messages = []
    received_message = s.recv(1024).decode('utf-8')
    while (len(received_message) == 1024):
        list_of_received_messages.append(received_message)
        received_message = s.recv(1024).decode('utf-8')
    list_of_received_messages.append(received_message)
    data = ''.join(list_of_received_messages)
    return data

# if reached end of total packets, only send remaining packets and not entire window
def set_window_size(num_packets):
    return min(N, num_packets - send_base)

# count the total number of retransmissions taking place
def calculate_retransmissions(dropped_packets):
    global retransmissions
    for _, val in dropped_packets.items():
        for i in range(1, val + 1):
            if i in retransmissions:
                retransmissions[i] += 1
            else:
                retransmissions[i] = 1

# probabilistically drop and store 1 % of the packets
def probabilistically_drop_packets(start, end, percentage):
    retransmissions = defaultdict(lambda: 0)
    if percentage == 0: percentage = 0.0001
    while start < end:
        if random.randint(1, 100/percentage) > 1:
            start += 1
        else:
            if start in retransmissions.keys():
                retransmissions[start] += 1
            else:
                retransmissions[start] = 1
    return retransmissions

# Send thread
def send(s):
    global mutex, send_base, send_timer, N, total_sent_packets, sent_packets

    if (printFlag): print("Sending sequence number from 1 to ", NUMBER_OF_PACKETS)
    send_base = 0 
    next_seq_no = 0
    
    # Start the receiver thread
    _thread.start_new_thread(receive, (s,))

    congestion_flag = False
    dropped_packets = probabilistically_drop_packets(0, NUMBER_OF_PACKETS, DROP_PROBABILITY)
    calculate_retransmissions(dropped_packets)
    sent_packets = set()

    while send_base < NUMBER_OF_PACKETS:
        mutex.acquire()
        while next_seq_no < send_base + N:
            if (printFlag): print('Sending packet with seq number ', next_seq_no)

            if dropped_packets[next_seq_no] == 0:
                socket_send(s, next_seq_no)
            else:
                dropped_packets[next_seq_no] -= 1
                    
            total_sent_packets += 1
            next_seq_no += 1

        # Start the timer
        if not send_timer.running():
            if (printFlag): print('Starting timer')
            send_timer.start()

        # Wait until a timer goes off or we get an ACK
        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            if (printFlag): print('Sleeping')
            time.sleep(0.005)
            mutex.acquire()

        # Handling timeout
        if send_timer.timeout():
            if (printFlag): print('Timeout')
            send_timer.stop()
            next_seq_no = send_base
            if (printFlag): print("window size changed from ", N, "to ", math.ceil(N/2))
            N = math.ceil(N/2)
            congestion_flag = True

        else:
            # happy scenario: received ack for sender base
            if (printFlag): print('Shifting window')
            if N < WRAP_AROUND:
                if not congestion_flag:
                    if (printFlag): print("window size changed from ", N, "to ", N * 2, " at ", next_seq_no)
                    N *= 2
                else:
                    if (printFlag): print("window size changed from ", N, "to ", N + 1, " at ", next_seq_no)
                    N += 1
            N = set_window_size(NUMBER_OF_PACKETS)
        mutex.release()

# Receive thread
def receive(s):
    global mutex, send_base, send_timer

    while True:
        ack_message = socket_receive(s)
        if (printFlag): print ("ack message received", ack_message)
        incoming_acks= [int(i) for i in ack_message.split(',')[:-1]]
        
        for ack in incoming_acks:
            # If we get an ACK for the first in-flight packet
            if (printFlag): print('Got ACK', ack)
            wrapped_ack_base = int(send_base % WRAP_AROUND)
            if (ack == wrapped_ack_base):
                mutex.acquire()
                send_base = send_base + 1
                if (printFlag): print('Base updated', send_base)
                send_timer.stop()
                mutex.release()


def main():

    global win_op

    start = datetime.now() # starting timer

    # creating graph data files   
    delete_file_if_already_exists("window_time.txt")
    win_op = open("window_time.txt", "a")
    write_in_file()

    # connecting to server and initiating handshake
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((HOST, PORT))
    # sending "nework" as a part of handshake
    s.send(b"network")
    data = s.recv(1024)

    # expecting "SUCCESS" as part of handshake
    if data.decode("utf-8") == "SUCCESS":
        if (printFlag): print(f"Received SUCCESS. Sending data")

        #start sending sequence numbers 
        send(s)

    # printing rubric variables
    print("Packets Sent\t->\t", total_sent_packets)
    
    print("Retransmissions Count")
    for key, val in retransmissions.items():
        print(key,"\t->\t",val)

    # calculating total program execution time
    end = datetime.now()
    print ("Total Execution Time \t->\t", end - start)

    # close and shutdown connections
    t.cancel()
    win_op.close()
    s.shutdown(SHUT_RDWR)
    s.close()


if __name__ == "__main__":
    main()