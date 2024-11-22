from mosquitto_connection import Mosquitto_Connection
from control import *
import time

controle_pid = PID_simple(kp=3, ki=2, kd=0.0, sample_time=0.1, saturation=100)

controle_pid.init_conection()

while True:
    controle_pid.receive_signal()
    controle_pid.calculate_PID()
    controle_pid.send_signal()
    print(f"y: {controle_pid._value} w: {controle_pid._reference} u: {controle_pid._control}")
    time.sleep(0.1)