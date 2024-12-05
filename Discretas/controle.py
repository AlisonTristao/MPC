from mosquitto_connection import *
from control import *
import time

controle = PID_Simple(kp=2, ki=2, kd=0.01)
controle.init_connection()

SAMPLE_TIME = 0.1

while True:
    start = time.time()
    controle.receive_signal()
    controle.calculate_u()
    controle.send_signal()
    time.sleep(max(0, SAMPLE_TIME - (time.time() - start)))