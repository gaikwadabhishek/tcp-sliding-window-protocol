import random

def generate_random_numbers_list(start, end, percentage):
     
    count = int((end * percentage)/100)
    total_count = count
    while (count > 0):
        count = int((count * percentage)/100)
        total_count += count
    print(total_count)
    random_numbers = random.sample(range(start, end), total_count)
    print(random_numbers)
    return random_numbers

generate_random_numbers_list(0, 100, 10)