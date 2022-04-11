import matplotlib.pyplot as plt
import numpy as np
x = []
y = []
for line in open('window_time.txt', 'r'):
    lines = [int(i) for i in line.split()]
    x.append(lines[0])
    y.append(int(lines[1]))
      
plt.title("WINDOW SIZE VS. TIME")
plt.xlabel('TIME IN SECONDS')
plt.ylabel('WINDOW SIZE')
plt.xticks(np.arange(0, 2500, 100))
plt.plot(x, y)

plt.show()
