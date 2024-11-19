import matplotlib.pyplot as plt
import random as ra
import numpy as np
import time

SAMPLE_TIME = 0.1

window_size = 50
x_data = np.zeros(1)
y1_data = x_data.copy()
y2_data = x_data.copy()
y3_data = x_data.copy()
y4_data = x_data.copy()

plt.ion()   # Modo interativo
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
plt.subplots_adjust(hspace=0.4)

line_y, = ax1.step([], [], lw=2, color='blue')
line_w, = ax1.step([], [], lw=1, color='purple', linestyle="--")
line_u, = ax2.step([], [], lw=2, color='orange')
line_q, = ax2.step([], [], lw=1, color='green', linestyle="--")

time_1 = ax1.axvline(x=x_data[-1], color='gray', linestyle='--')
time_2 = ax2.axvline(x=x_data[-1], color='gray', linestyle='--')

ax1.title.set_text('y(k) and w(k)')
ax2.title.set_text('u(k) and q(k)')
ax1.set_xlim(0, 2*window_size)
ax1.set_ylim(0, 1)
ax1.grid(True, linestyle="--")

ax2.set_xlim(0, 2*window_size)
ax2.set_ylim(0, 1)
ax2.grid(True, linestyle="--")

start_time = 0

while True:
    start_time = time.time()

    x_data = np.append(x_data, x_data[-1] + 1)
    y1_data = np.append(y1_data, ra.random())
    y2_data = np.append(y2_data, ra.random())
    y3_data = np.append(y3_data, ra.random())
    y4_data = np.append(y4_data, ra.random())

    if len(x_data) > window_size:
        x_data = x_data[-window_size:]  # Mantém apenas os últimos valores
        y1_data = y1_data[-window_size:]
        y2_data = y2_data[-window_size:]
        y3_data = y3_data[-window_size:]
        y4_data = y4_data[-window_size:]

    line_y.set_xdata(x_data)
    line_y.set_ydata(y1_data)
    line_u.set_xdata(x_data)
    line_u.set_ydata(y2_data)
    line_w.set_xdata(x_data)
    line_w.set_ydata(y3_data)
    line_q.set_xdata(x_data)
    line_q.set_ydata(y4_data)

    time_1.set_xdata([x_data[-1]])
    time_2.set_xdata([x_data[-1]])

    ax1.set_xlim(x_data[0], x_data[0] + 2*window_size)
    ax2.set_xlim(x_data[0], x_data[0] + 2*window_size)

    plt.pause(SAMPLE_TIME - (time.time() - start_time))