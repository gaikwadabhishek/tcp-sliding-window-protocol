import matplotlib.pyplot as plt
  
x = []
y = []
for line in open('seqno_time.txt', 'r'):
    lines = [i for i in line.split()]
    x.append(lines[0])
    y.append(int(lines[1]))
      
plt.title("Sequence numbers over time")
plt.xlabel('Time in seconds')
plt.ylabel('Sequence numbers')
plt.yticks(y)
plt.plot(x, y, marker = 'o', c = 'g')

plt.show()
