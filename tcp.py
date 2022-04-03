import socket
import random
import math

from config import DROP_PROBABILITY, WRAP_AROUND

def send(s, next_seq_no):
    if next_seq_no > 0:
        if random.randint(0, 99) > 0:
            next_seq_no = int(next_seq_no % WRAP_AROUND)
            s.send((str(next_seq_no) + ",").encode('utf-8'))
    else:
        s.send((str(next_seq_no) + ",").encode('utf-8'))

def receive(s):
    list_of_received_messages = []
    received_message = s.recv(1024).decode('utf-8')
    while (len(received_message) == 1024):
        list_of_received_messages.append(received_message)
        received_message = s.recv(1024).decode('utf-8')
    list_of_received_messages.append(received_message)
    data = ''.join(list_of_received_messages)
    return data