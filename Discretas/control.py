from mosquitto_connection import Mosquitto_Connection
import numpy as np

class Control:
    # mosquitto connection default values
    _topic_receive  = "plant_simulation"
    _topic_send     = "control_simulation"
    _client_id      = "control"

    # control default values
    _control        =  0.0
    _y              =  0.0
    _reference      =  [0]  
    _saturation     =  100

    #def __init__(self):
        #raise NotImplementedError("function not implemented")

    def init_conection(self):
        self._connection = Mosquitto_Connection(
            topic_receive=self._topic_receive,
            topic_send=self._topic_send,
            client_id=self._client_id
        )
        print("Conexão com Mosquitto estabelecida")
    
    def change_topics(self, topic_receive=_topic_receive, topic_send=_topic_send, client_id=_client_id):
        self._topic_receive = topic_receive
        self._topic_send    = topic_send
        self._client_id     = client_id

    def send_signal(self, u):
        self._connection.send_package(u=u)
    
    def receive_signal(self):
        self._connection.receive_package()
        if self._connection.get_value("y") is not None:
            self._y = self._connection.get_value("y")

        if self._connection.get_value("w") is not None:
            self._reference = self._connection.get_value("w")

class PID_simple(Control):
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, sample_time=0.01, saturation=100):   
        self._sample_time   = sample_time
        self._saturarion    = saturation
        self._kp            = kp
        self._ki            = ki
        self._kd            = kd
        self._integral      = 0.0
        self._derivative    = 0.0
        self._last_y        = 0.0
        self._error         = 0.0

    def send_signal(self):
        self._connection.send_package(u=self._control)

    def calculate_PID(self):
        # calculates error
        self._error = self._reference[0] - self._y

        # calculates integral
        self._integral += self._error * self._sample_time

        # saturate integral
        if self._integral > self._saturation:
            self._integral = self._saturation
        elif self._integral < -self._saturation:
            self._integral = -self._saturation

        # calculate derivative
        self._derivative = (self._y - self._last_y)/self._sample_time

        # saturate derivative
        '''if self._derivative > self._saturation/2:
            self._derivative = self._saturation/2
        elif self._derivative < -self._saturation/2:
            self._derivative = -self._saturation/2'''

        # safe last error
        self._last_y = self._y

        # calculate control
        self._control = self._kp * self._error + self._ki * self._integral + self._kd * self._derivative
        
        # saturate control
        if self._control > self._saturation: 
            self._control = self._saturation
        elif self._control < -self._saturation:
            self._control = -self._saturation   
    
class PID_with_future_reference(PID_simple):
    # observe that the future_reference is a list of values
    def __moving_average(self, future_reference, n):
        mediam = 0
        for j in range(n):
            mediam += future_reference[j]
        return mediam/n
        
    def calculate_PID_ref_future(self, future_reference_arr,  horizon=1):
        ref_filt = self.__moving_average(future_reference_arr, horizon)
        self._reference = ref_filt
        self.calculate_PID(self._error)