import socket
import random
import math

from config import DROP_PROBABILITY, WRAP_AROUND

def send(s, next_seq_no):
    # if random.randint(0, 100) > 0:
    next_seq_no = int(next_seq_no % WRAP_AROUND)
    s.send((str(next_seq_no) + ",").encode('utf-8'))

def receive(s):
    return s.recv(100000).decode('utf-8')