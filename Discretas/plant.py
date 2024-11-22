import mosquitto_connection as mosquitto_connection
import numpy as np

class Plant:
    _topic_receive  = "control_simulation"
    _topic_send     = "plant_simulation"
    _client_id      = "plant"
    __value         = 0.0
    __u             = 0.0
    __alpha         = [0.8]
    __b             = [1.0]

    def __init__(self, alpha=[0.8], b=[1.0]):
        self.__alpha = alpha
        self.__b = b

        if len(self.__alpha) != len(self.__b):
            raise ValueError("alpha and b must have the same length")
                 
    def init_conection(self):
        self._connection = mosquitto_connection.Mosquitto_Connection(
            topic_receive=self._topic_receive,
            topic_send=self._topic_send,
            client_id=self._client_id
        )

    def change_topics(self, topic_receive=_topic_receive, topic_send=_topic_send, client_id=_client_id):
        self._topic_receive = topic_receive
        self._topic_send    = topic_send
        self._client_id     = client_id

    def receive_signal(self):
        self._connection.receive_package()
        if self._connection.get_value("u") is not None:
            self.__u = self._connection.get_value("u")

    def send_signal(self, w=[0.0]):
        self._connection.send_package(y=self.__value, w=w)

    def plant_step_simulation(self):
        for i in range(len(self.__alpha)):
            self.__value = self.__alpha[i] * self.__value + self.__b[i] * self.__u

    def get_y(self):
        return self.__value 