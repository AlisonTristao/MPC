from mosquitto_connection import Mosquitto_Connection
import random
import time

# Create a connection to the broker
connection = Mosquitto_Connection(
    topic_receive   = "cliente_1",
    topic_send      = "cliente_2",
    client_id       = "receiver"
)

# Envia pacote
counter = 0
while True:
    connection.send_package(
            recebido=counter
    )

    # Recebe pacote
    connection.receive_package()
    print(connection.get_value("enviado"), counter)

    #time.sleep(0.1)

    counter += 1

    if counter == 100:
        break

# Close the connection
connection.close()