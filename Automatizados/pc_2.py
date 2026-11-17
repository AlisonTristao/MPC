import random
from mosquitto_connection import *
from simulation import *
from plant import *


window_size = 10
config_to_plot = {
        "data_config":{"y": [1],"u": [2]},
        "data_colors":{"y": "orange","u": "green"},   
        "data_style":{"y": "-","u": "-"},
        "data_win":{"y": window_size,"u": window_size}
}

simulation = Simulation(config_to_plot)
simulation.plant_configurations(alpha=[0.6, 0.3], beta=[0.1], gama=[0.1], saturation=100)

w = 50
q = 0

while True:
    if random.randint(0, 1000) < 50:
        w = int(random.uniform(-50, 50))
 
    if random.randint(0, 1000) < 10:
        q = int(random.uniform(-50, 50))

    simulation.step(w, q, noise=0.01, w_horizon=10)