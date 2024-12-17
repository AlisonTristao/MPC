from mosquitto_connection import Mosquitto_Connection
import random

class Plant:
    _topic_receive = "control_simulation/u"
    _topic_send = "plant_simulation/y"
    _client_id = "plant"

    def __init__(self, alpha=[0.9], beta=[1], gama=[1], saturation=100):
        self.__alpha = [alpha[len(alpha) - 1 - i] for i in range(len(alpha))]
        self.__beta = [beta[len(beta) - 1 - i] for i in range(len(beta))]
        self.__gama = [gama[len(gama) - 1 - i] for i in range(len(gama))]
        self.__y = [0 for _ in range(len(alpha))]
        self.__u = [0 for _ in range(len(beta))]
        self.__q = [0 for _ in range(len(gama))]
        self.__saturation = saturation

    def init_connection(self):
        self.__connection = Mosquitto_Connection(
            topic_receive=self._topic_receive,
            topic_send=self._topic_send,
            client_id=self._client_id
        )
        print("Mosquitto connection established.")

    def change_topics(self, topic_receive=_topic_receive, topic_send=_topic_send, client_id=_client_id):
        self._topic_receive = topic_receive
        self._topic_send = topic_send
        self._client_id = client_id

    def receive_signal(self):
        self.__connection.receive_package()
        if self.__connection.get_value("u") is not None:
            self.__u.append(self.__connection.get_value("u"))
            self.__u = self.__u[1:]

    def step_simulation(self, q=0, noise=0):
        # add perturbation
        self.__q.append(q)
        self.__q = self.__q[1:]

        # calculate y response
        y = 0
        y += sum(self.__y[i] * self.__alpha[i] for i in range(len(self.__y)))
        y += sum(self.__u[i] * self.__beta[i] for i in range(len(self.__u)))
        y += sum(self.__q[i] * self.__gama[i] for i in range(len(self.__q)))
        
        # add noise with value noise * saturation
        y += random.uniform(-noise * self.__saturation, noise * self.__saturation)

        # saturate y
        y = min(y, self.__saturation)
        y = max(y, -self.__saturation)

        self.__y.append(y)
        self.__y = self.__y[1:]

    def send_signal(self, w=[0.0], q=[0.0]):
        self.__connection.send_package(y=self.__y[0], w=w, q=q)

    def set_w(self, w):
        self.__w = w

    def get_y(self):
        return self.__y[-1]

    def get_u(self):
        return self.__u[-1]
    
    def get_q(self):
        return self.__q[-1]
    
    def get_data(self):
        data = {
            'y': self.get_y(),
            'u': self.get_u()
        }

        return data