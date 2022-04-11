import random


def generate_random_numbers(start, end, percentage):
    retransmissions = {}
    while start < end:
        if random.randint(1, 100/percentage) > 1:
            start += 1
        else:
            if start in retransmissions.keys():
                retransmissions[start] += 1
            else:
                retransmissions[start] = 1
    return retransmissions

