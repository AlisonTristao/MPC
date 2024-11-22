from mosquitto_connection import Mosquitto_Connection
from plant import *

plant = Plant(alpha=[0.2, 0.3], b=[0.1, 0.2])

plant.init_conection()
plant._connection.set_wait_time(0.2)

while True:
    plant.send_signal(w=[2.0])
    plant.plant_step_simulation()
    plant.receive_signal()
    print(plant.get_y())
    #time.sleep(1)