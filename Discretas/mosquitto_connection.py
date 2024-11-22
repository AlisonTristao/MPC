import paho.mqtt.client as mqtt
import time
import ujson

class Mosquitto_Connection:
    def __init__(self, topic_send, topic_receive, client_id, port=1883, broker="localhost"):
        self.__package = None
        self.__received = False
        self.__broker = broker
        self.__port = port
        self.__topic_send = topic_send
        self.__topic_receive = topic_receive
        self.__client_id = client_id
        self.__wait_time = 0.11
        self.__converter = JSON_Converter()
        self.__client = mqtt.Client(client_id=self.__client_id, protocol=mqtt.MQTTv311)
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.connect(self.__broker, self.__port, 60)
        self.__client.loop_start()

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.__topic_receive)
        else:
            print(f"Connection failed: {rc}")

    def __on_message(self, client, userdata, msg):
        try:
            self.__package = msg.payload.decode()
            self.__received = True
        except Exception as e:
            print(f"Error receiving package: {e}")

    def __is_received(self):
        return self.__received

    def set_wait_time(self, wait_time):
        self.__wait_time = wait_time

    def __wait_for_package(self):
        timer = time.time()
        while not self.__is_received():
            if time.time() - timer > self.__wait_time:
                print("Timeout waiting for package.")
                break
        self.__received = False

    def __publish(self, package):
        try:
            self.__client.publish(self.__topic_send, package)
        except Exception as e:
            print(f"Error publishing package: {e}")

    def send_package(self, **kwargs):
        self.__converter.data = {}
        self.__converter.add_values(**kwargs)
        self.__publish(self.__converter.to_json())

    def receive_package(self):
        self.__wait_for_package()
        if self.__package is not None:
            self.__converter.from_json(self.__package)

    def get_value(self, key):
        value = self.__converter.get_value(key)
        if value is None:
            print(f"Key not found: {key}")
        return value

    def close(self):
        try:
            self.__client.loop_stop()
            self.__client.disconnect()
        except Exception as e:
            print(f"Error closing connection: {e}")

class JSON_Converter:
    def __init__(self):
        self.data = {}

    def add_values(self, **kwargs):
        self.data.update(kwargs)

    def to_json(self):
        return ujson.dumps(self.data)

    def from_json(self, json_string):
        try:
            self.data = ujson.loads(json_string)
        except ValueError as e:
            print(f"Error converting JSON to dictionary: {e}")

    def get_data(self):
        return self.data

    def get_value(self, key):
        return self.data.get(key)
    
# Teste
'''if __name__ == "__main__":
    try:
        # Cria conexão
        print("Testando conexão com Mosquitto...")

        # Cria conexão
        connection = Mosquitto_Connection(
            broker="localhost",
            port=1883,
            topic="test",
            client_id="test"
        )

        # Envia pacote
        connection.send_package(
            temperature=[25.0, 26.0, 27.0],
            humidity=[50.0, 51.0, 52.0],
        )

        # Recebe pacote
        connection.receive_package()

        # Exibe valores
        print(connection.get_value("temperature"))
        print(connection.get_value("humidity"))

        # Encerra conexão
        connection.close()

    except Exception as e:
        print(f"Erro: {e}")'''