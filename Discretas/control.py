from mosquitto_connection import Mosquitto_Connection

class Control:
    _topic_receive = "plant_simulation/y"
    _topic_send = "control_simulation/u"
    _client_id = "control"
    _control = 0.0
    _saturation = 100
    _y = 0.0
    _reference = [0]

    def init_connection(self):
        self._connection = Mosquitto_Connection(
            topic_receive=self._topic_receive,
            topic_send=self._topic_send,
            client_id=self._client_id
        )
        print("Mosquitto connection established.")

    def change_topics(self, topic_receive=_topic_receive, topic_send=_topic_send, client_id=_client_id):
        self._topic_receive = topic_receive
        self._topic_send = topic_send
        self._client_id = client_id

    def send_signal(self, u):
        self._connection.send_package(u=u)

    def receive_signal(self):
        self._connection.receive_package()
        if self._connection.get_value("y") is not None:
            self._y = self._connection.get_value("y")
        if self._connection.get_value("w") is not None:
            self._reference = self._connection.get_value("w")

class PID_Simple(Control):
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, sample_time=0.1, saturation=100):
        self._sample_time = sample_time
        self._saturation = saturation
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._integral = 0.0
        self._derivative = 0.0
        self._last_y = 0.0
        self._error = 0.0
        self._previous_control = 0.0

    def send_signal(self):
        self._connection.send_package(u=self._control)

    def calculate_u(self):
        self._error = self._reference[0] - self._y
        self._integral += self._error * self._sample_time

        unsaturated_control = self._kp * self._error + self._ki * self._integral + self._kd * self._derivative
        self._control = max(min(unsaturated_control, self._saturation), -self._saturation)

        if self._control != unsaturated_control:
            self._integral -= self._error * self._sample_time

        self._derivative = (self._y - self._last_y) / self._sample_time
        self._last_y = self._y

class PID_With_Future_Reference(PID_Simple):
    def __moving_average(self, future_reference, n):
        if len(future_reference) < n:
            print("Not enough future reference values.")
        return sum(future_reference[:n]) / n

    def calculate_u(self, horizon=1):
        filtered_ref = self.__moving_average(self._reference, horizon)
        self._reference[0] = filtered_ref
        super().calculate_u()
