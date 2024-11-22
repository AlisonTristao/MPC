import random
from mosquitto_connection import *
from realtime_plot import *
from plant import *

planta = Plant(alpha=[0.6, 0.3], beta=[0.1], gama=[0.1])
planta.init_connection()

plotter = Realtime_Plot()

w = 50  
q = 10
step_count_ref = 0 
step_count_q = 0

while True:
    step_count_ref += 1
    step_count_q += 1

    if step_count_ref == 60:
        step_count_ref = 0
        w = random.uniform(-100, 100) 

    if step_count_q == 120:
        step_count_q = 0
        q = random.uniform(-25, 25)

    planta.receive_signal()
    planta.step_simulation(q=q, noise=0.01)
    planta.send_signal(w=[w])

    plotter.step(planta.get_data())

