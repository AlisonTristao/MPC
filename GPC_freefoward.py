import numpy as np
import matplotlib.pyplot as plt

SAMPLE = 1

alpha = 0.9
b = 0.05

y = np.zeros(100)
u = np.concatenate((np.ones(50), np.zeros(50)))

for i in range(1, 100):
    y[i] = alpha*y[i-1] + b * u[i-1]

plt.plot(y)
plt.grid()
plt.show()
