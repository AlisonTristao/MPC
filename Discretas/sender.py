from mosquitto_connection import Mosquitto_Connection
import random
import time

# Cria conexão
print("Testando conexão com Mosquitto...")
connection = Mosquitto_Connection(
    topic_receive   = "cliente_2",
    topic_send      = "cliente_1",
    client_id       = "sender"
)

# Envia pacote
counter = 0
while True:
    connection.send_package(
            enviado=counter,
    )

    # Recebe pacote
    connection.receive_package()
    print(connection.get_value("recebido"), counter)

    time.sleep(0.1)

    counter += 1
