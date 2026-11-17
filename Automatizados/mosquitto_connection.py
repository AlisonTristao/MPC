import time
import threading
import ujson
import zmq
import hashlib
import sys

def _port_from_topic(topic: str, base: int = 20000, span: int = 9000) -> int:
    """
    Porta TCP estável a partir do nome do tópico.
    Faixa: [base, base+span). Evita colisões entre tópicos diferentes.
    """
    h = hashlib.sha256(topic.encode()).digest()
    n = int.from_bytes(h[:4], "big") % span
    return base + n

class Mosquitto_Connection:
    """
    Compatível com a API anterior, mas sem Mosquitto/MQTT.
    Usa ZeroMQ (brokerless) no loopback.

    Mantém:
      - set_wait_time(wait_time)
      - send_package(**kwargs)
      - receive_package()
      - get_value(key)
      - close()

    __init__(topic_send, topic_receive, client_id, port=1883)
    (os argumentos são aceitos para compatibilidade; 'port' é ignorado)
    """

    def __init__(self, topic_send, topic_receive, client_id, port=1883):  # compat
        self.__package = None
        self.__received = False
        self.__topic_send = str(topic_send)
        self.__topic_receive = str(topic_receive)
        self.__client_id = str(client_id)
        self.__wait_time = 2.0
        self.__converter = JSON_Converter()

        # Endpoints TCP determinísticos (127.0.0.1:<porta calculada>)
        self.__pub_endpoint = f"tcp://127.0.0.1:{_port_from_topic(self.__topic_send)}"
        self.__sub_endpoint = f"tcp://127.0.0.1:{_port_from_topic(self.__topic_receive)}"

        # Contexto ZMQ
        self.__ctx = zmq.Context.instance()

        # PUB para enviar no topic_send (faz bind)
        self.__pub = self.__ctx.socket(zmq.PUB)
        # Conflito de bind? muito improvável pois cada side binda seu próprio tópico.
        self.__pub.setsockopt(zmq.LINGER, 0)
        self.__pub.bind(self.__pub_endpoint)

        # SUB para receber do topic_receive (faz connect)
        self.__sub = self.__ctx.socket(zmq.SUB)
        self.__sub.setsockopt(zmq.LINGER, 0)
        # No ZMQ, SUBSCRIBE é um prefixo textual; aqui usamos o tópico exato
        self.__sub.setsockopt_string(zmq.SUBSCRIBE, self.__topic_receive)
        self.__sub.connect(self.__sub_endpoint)

        # Thread de recepção
        self.__stop_evt = threading.Event()
        self.__rx_thread = threading.Thread(target=self.__rx_loop, daemon=True)
        self.__rx_thread.start()

        # “warm-up” para o handshake PUB/SUB
        time.sleep(0.1)

    # ===== Internos =====
    def __rx_loop(self):
        poller = zmq.Poller()
        poller.register(self.__sub, zmq.POLLIN)
        while not self.__stop_evt.is_set():
            events = dict(poller.poll(timeout=100))
            if self.__sub in events:
                try:
                    raw = self.__sub.recv_string(flags=zmq.NOBLOCK)
                    # Formato: "<topic> <json>"
                    topic, payload = raw.split(" ", 1)
                    if topic == self.__topic_receive:
                        self.__package = payload
                        self.__received = True
                except zmq.Again:
                    pass
                except Exception as e:
                    print(f"Erro recebendo: {e}", file=sys.stderr)

    def __is_received(self):
        return self.__received

    def __wait_for_package(self):
        timer = time.time()
        while not self.__is_received():
            if time.time() - timer > self.__wait_time:
                print("Timeout esperando pacote.")
                break
            time.sleep(0.003)
        got = self.__received
        self.__received = False
        return got

    def __publish(self, package: str):
        try:
            # Envia como "<topic> <json>"
            self.__pub.send_string(f"{self.__topic_send} {package}")
        except Exception as e:
            print(f"Erro ao publicar pacote: {e}", file=sys.stderr)

    # ===== API pública idêntica =====
    def set_wait_time(self, wait_time):
        self.__wait_time = float(wait_time)

    def send_package(self, **kwargs):
        self.__converter.data = {}
        self.__converter.add_values(**kwargs)
        self.__publish(self.__converter.to_json())

    def receive_package(self):
        ok = self.__wait_for_package()
        if ok and self.__package is not None:
            self.__converter.from_json(self.__package)

    def get_value(self, key):
        value = self.__converter.get_value(key)
        if value is None:
            print(f"Key not found: {key}")
        return value

    def close(self):
        try:
            self.__stop_evt.set()
            if self.__rx_thread.is_alive():
                self.__rx_thread.join(timeout=0.5)
        except Exception as e:
            print(f"Erro encerrando thread: {e}", file=sys.stderr)
        try:
            self.__sub.close(0)
            self.__pub.close(0)
        except Exception as e:
            print(f"Erro fechando sockets: {e}", file=sys.stderr)
        # Não fecho o Context global (instance) para não afetar outros usuários ZMQ.

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
