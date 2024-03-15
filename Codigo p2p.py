import socket
import threading

# Función para manejar la comunicación con un cliente específico
def handle_client(client_socket, client_address):
    print(f"Conexión establecida con {client_address}")

    while True:
        try:
            # Recibir mensaje del cliente
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break
            print(f"Mensaje recibido de {client_address}: {data}")

            # Reenviar mensaje a todos los clientes conectados
            broadcast(data, client_socket)
        except ConnectionResetError:
            break

    print(f"Conexión cerrada con {client_address}")
    client_socket.close()

# Función para reenviar mensajes a todos los clientes excepto al remitente
def broadcast(message, sender_socket):
    for client in clients:
        client_socket, _ = client
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode("utf-8"))
            except ConnectionResetError:
                clients.remove(client)

# Configuración del servidor/cliente
HOST = '0.0.0.0'  # Escuchar en todas las interfaces de red
PORT = 872

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"Servidor/Cliente escuchando en el puerto {PORT}...")

clients = []

# Manejo de conexiones entrantes
def accept_connections():
    while True:
        client_socket, client_address = server.accept()

        # Verificar si la dirección IP está dentro del rango especificado
        ip_prefix = '192.168.2.'
        if client_address[0].startswith(ip_prefix):
            clients.append((client_socket, client_address))

            # Mostrar las conexiones disponibles
            print("Conexiones disponibles:")
            for idx, (_, addr) in enumerate(clients):
                print(f"{idx}: {addr}")

            # Crear un hilo para manejar la comunicación con el nuevo cliente
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        else:
            print(f"Conexión desde {client_address} rechazada: Fuera del rango permitido.")

# Iniciar un hilo para manejar conexiones entrantes
accept_thread = threading.Thread(target=accept_connections)
accept_thread.start()

# Función para enviar mensajes a una dirección IP específica
def send_message():
    while True:
        try:
            if not clients:
                print("No hay clientes conectados.")
                break

            idx = int(input("Seleccione el índice de la conexión a la que desea enviar el mensaje: "))
            if 0 <= idx < len(clients):
                message = input("Ingrese el mensaje que desea enviar: ")
                if message.lower() == "exit":
                    break
                client_socket, _ = clients[idx]
                client_socket.send(message.encode("utf-8"))
            else:
                print("Índice fuera de rango.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

# Iniciar un hilo para enviar mensajes
send_thread = threading.Thread(target=send_message)
send_thread.start()
