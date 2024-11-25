import random
from mosquitto_connection import *
from simulation import *
from plant import *

window_size = 50
config_to_plot = {
        "data_config":{"y": [1],"w": [2],"u": [3],"q": [4]},
        "data_colors":{"y": "orange","w": "purple","u": "green","q": "black"},   
        "data_style":{"y": "-","w": "--","u": "-","q": "--"},
        "data_win":{"y": window_size,"w": int(2 * window_size),"u": window_size,"q": 2*window_size}
}

simulation = Simulation(config_to_plot)
simulation.plant_configurations(alpha=[0.6, 0.3], beta=[0.1], gama=[0.1], saturation=100)

w = 50  
q = 0
step_count_ref = 0 
step_count_q = 0

while True:
    step_count_ref += 1
    step_count_q += 1

    if step_count_ref == 60:
        step_count_ref = 0
        w = int(random.uniform(-100, 100)) 

    if step_count_q == 120:
        step_count_q = 0
        q = int(random.uniform(-25, 25))

    simulation.step(w, q, horizon=5)
