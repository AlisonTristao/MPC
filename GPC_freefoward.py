import numpy as np
import matplotlib.pyplot as plt

from solver_Axb import matrix_G

SAMPLE = 1

alpha = 0.9
b = 0.1

y0 = np.zeros(100)
u = np.concatenate((np.ones(50), np.zeros(50)))

delta_u = np.zeros(100)
delta_u[1] = 1
delta_u[51] = -1 

G = matrix_G(100, alpha)
y1 = G @ delta_u

for i in range(1, 100):
    y0[i] = alpha*y0[i-1] + b * u[i-1]

plt.plot(y0, label="y0")
plt.plot(y1, label="y1", linestyle="--")
plt.legend()
plt.grid()
plt.show()
