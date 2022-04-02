import socket
import random

from config import DROP_PROBABILITY

def send(s, next_seq_no):
    if random.randint(0, DROP_PROBABILITY) > 0:
        s.send((str(next_seq_no) + ",").encode('utf-8'))

def receive(s):
    return s.recv(1024).decode('utf-8')