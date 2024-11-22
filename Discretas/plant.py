import mosquitto_connection as mosquitto_connection

class Plant:
    _topic_receive  = "control_simulation"
    _topic_send     = "plant_simulation"
    _client_id      = "plant"
    
    def __init__(self, alpha=[0.9], beta=[1]):
        # reverse alpha and beta for the convolution 
        self.__alpha    = [alpha[len(alpha) - 1 - i] for i in range(len(alpha))]
        self.__beta     = [beta[len(beta) - 1 - i] for i in range(len(beta))]
        self.__y        = [0 for _ in range(len(alpha))]
        self.__u        = [0 for _ in range(len(beta))]

        
    def init_conection(self):
        self.__connection = mosquitto_connection.Mosquitto_Connection(
            topic_receive=self._topic_receive,
            topic_send=self._topic_send,
            client_id=self._client_id
        )
        print("Conexão com Mosquitto estabelecida")

    def change_topics(self, topic_receive=_topic_receive, topic_send=_topic_send, client_id=_client_id):
        self._topic_receive = topic_receive
        self._topic_send    = topic_send
        self._client_id     = client_id

    def receive_signal(self):
        self.__connection.receive_package()
        if self.__connection.get_value("u") is not None:
            self.__u.append(self.__connection.get_value("u"))
            self.__u = self.__u[1:]

    def step_simulation(self):
        y = 0
        # sum y past values
        for i in range(len(self.__y)):
            y += self.__y[i] * self.__alpha[i]

        # sum u past values
        for i in range(len(self.__u)):
            y += self.__u[i] * self.__beta[i]

        # calculate new y
        self.__y.append(y)
        self.__y = self.__y[1:]
        
    def send_signal(self, w=[0.0]):
        self.__connection.send_package(y=self.__y[0], w=w)

    def get_y(self):
        return self.__y[len(self.__y) - 1]