import paho.mqtt.client as mqtt
import time as t
import ujson

# Classe para conexão com Mosquitto
class Mosquitto_Connection:
    def __init__(self, topic_send, topic_receive, client_id, port=1883, broker = "localhost"):
        self.__package          = None              # string json recebida
        self.__received         = False             # flag de recebimento de pacote
        self.__broker           = broker            # endereço de onde estao os dados
        self.__port             = port              # porta de conexão
        self.__topic_send       = topic_send        # tópico de envio
        self.__topic_receive    = topic_receive     # tópico de recebimento
        self.__client_id        = client_id         # id do cliente
        self.__wait_time        = 0.5               # tempo de espera para recebimento de pacote
        self.__converter        = JSONConverter()   # conversor de JSON para dicionário
        
        # cliente mosquitto 
        self.__client = mqtt.Client(
                        client_id=self.__client_id, 
                        protocol=mqtt.MQTTv311
                    )

        # metodos de callback para conexão e recebimento de mensagens
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        
        # conecta ao instanciar a classe
        self.__client.connect(self.__broker, self.__port, 60)
        self.__client.loop_start()

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            #print("Conexão bem-sucedida!")
            client.subscribe(self.__topic_receive)
        else:
            print(f"Fail: {rc}")

    def __on_message(self, client, userdata, msg):
        try:
            self.__package = msg.payload.decode()
            self.__received = True
            #print(f"Pacote recebido: {self.__package}")
        except Exception as e:
            print(f"Error to receive package: {e}")
        
    def __is_received(self):
        return self.__received
    
    def set_wait_time(self, wait_time):
        self.__wait_time = wait_time
    
    def __wait_for_package(self):
        timer = t.time()
        # Aguarda pacote por 0.1 segundos
        while not self.__is_received():
            if t.time() - timer > self.__wait_time:
                print(f"Time to wait for package expired!")
                break
        self.__received = False

    def __publish(self, package):
        try:
            self.__client.publish(self.__topic_send, package)
            #print(f"Pacote '{package}' publicado no tópico '{self.__topic}'")
        except Exception as e:
            print(f"Error to publish package: {e}")

    def send_package(self, **kwargs):
        # zera os valores do dicionário
        self.__converter.data = {}
        self.__converter.add_values(**kwargs)
        self.__publish(self.__converter.to_json())

    def receive_package(self):
        # zerar o pacote
        self.__package = None
        self.__converter.data = {}

        # Aguarda pacote
        self.__wait_for_package()
            
        # Recebe pacote
        if self.__package is not None:
            self.__converter.from_json(self.__package)

    def get_value(self, key):
        value = self.__converter.get_value(key)
        if value is None:
            print(f"Key not found! {key}")
        return value

    def close(self):
        try:
            self.__client.loop_stop()
            self.__client.disconnect()
            #print("Conexão encerrada!")
        except Exception as e:
            print(f"Error to close connection: {e}")

class JSONConverter:
    def __init__(self):
        self.data = {} 

    def add_values(self, **kwargs):
        self.data.update(kwargs)

    def to_json(self):
        '''self.inser_checksum()'''
        return ujson.dumps(self.data)

    def from_json(self, json_string):
        try:
            self.data = ujson.loads(json_string)
            # verifica o checksum
            '''if not self.verify_checksum():
                print("Checksum invalid", self.data)
                return'''
        except ValueError as e:
            print("Error to convert JSON to dictionary: {e}")

    def get_data(self):
        return self.data
    
    def get_value(self, key):
        return self.data.get(key, None)
    
    '''def inser_checksum(self):
        checksum = 0
        for key, value in self.data.items():
            if key != "checksum":
                checksum += value
        self.data["checksum"] = checksum
        print(f"Checksum: {checksum}")

    def verify_checksum(self):
        checksum = self.data.get("checksum", None)
        if checksum is None:
            print("Checksum not found!")
            return False
        
        # Verifica checksum
        for key, value in self.data.items():
            if key != "checksum":
                checksum -= value

        return checksum == 0'''
        
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