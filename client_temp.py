import _thread
import threading
import time
import socket
from config import NUMBER_OF_PACKETS, WRAP_AROUND
import math
from socket import SHUT_RDWR
from datetime import datetime
from tcp_server import delete_file_if_already_exists
import random

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
cntr = 1
win_op = None

# Shared resources across threads
send_base = 0
mutex = _thread.allocate_lock()
send_timer = Timer(0.2)
N = 1 # window size
total_sent_packets = 0
total_retransmissions = {}
retransmissions = {}
printFlag = False


def write_in_file():
    global cntr
    global t
    global win_op
    t = threading.Timer(1, write_in_file)
    t.start()
    win_op.write(f"{cntr} {N}\n")
    cntr += 1


# sending pakcets using socket connection and probablistically dropping packets
def socket_send(s, next_seq_no):
    if random.randint(0, 399) > 0:
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

# Send thread
def send(s):
    global mutex
    global send_base
    global send_timer
    global N
    global total_sent_packets
    global retransmissions

    if (printFlag): print("Sending sequence number from 1 to ", NUMBER_OF_PACKETS)
    send_base = 0 
    next_seq_no = 0
    
    # Start the receiver thread
    _thread.start_new_thread(receive, (s,))

    congestion_flag = False

    while send_base < NUMBER_OF_PACKETS:
        mutex.acquire()
        while next_seq_no < send_base + N:
            if (printFlag): print('Sending packet with seq number ', next_seq_no)
            if next_seq_no in retransmissions:
                retransmissions[next_seq_no] += 1
            else:
                retransmissions[next_seq_no] = 1
            socket_send(s, next_seq_no)
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
            time.sleep(0.05)
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
                    N += 10
            N = set_window_size(NUMBER_OF_PACKETS)
        mutex.release()

# Receive thread
def receive(s):
    global mutex
    global send_base
    global send_timer

    while True:
        ack_message = socket_receive(s)
        if (printFlag): print ("ack message received", ack_message)
        incoming_acks= [int(i) for i in ack_message.split(',')[:-1]]
        
        for ack in incoming_acks:
            # If we get an ACK for the first in-flight packet
            if (printFlag): print('Got ACK', ack)
            wrapped_ack_base = int(send_base % WRAP_AROUND)
            if (ack >= wrapped_ack_base):
                mutex.acquire()
                send_base = send_base + 1
                if (printFlag): print('Base updated', send_base)
                send_timer.stop()
                mutex.release()

# calculating retransmissions
def calculate_retransmissions():
    global total_retransmissions
    for i in retransmissions.keys():
        if retransmissions[i] in total_retransmissions:
            total_retransmissions[retransmissions[i]] += 1
        else:
            total_retransmissions[retransmissions[i]] = 1
    
    for i in total_retransmissions.keys():
        for j in range(1, i):
            total_retransmissions[j] += total_retransmissions[i]

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
    s.send(b"network")
    data = s.recv(1024)

    if data.decode("utf-8") == "SUCCESS":
        print(f"Received SUCCESS. Sending data")

        #start sending sequence numbers 
        send(s)

    # printing rubric variables
    print("total packets sent ->", total_sent_packets)
    calculate_retransmissions()
    print("total retransmissions ->")
    for key, val in total_retransmissions.items():
        print(key, val)

    # calculating total program execution time
    end = datetime.now()
    print ("total_time -> ", end - start)

    # close and shutdown connections
    t.cancel()
    win_op.close()
    s.shutdown(SHUT_RDWR)
    s.close()


if __name__ == "__main__":
    main()