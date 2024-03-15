import socket
import threading
import time

# Constantes
UDP_PORT = 5001
DISCOVERY_SERVER = ("localhost", 5000)
MESSAGE_INTERVAL = 5
MESSAGE = b"Hola desde Copilot"

# Lista para guardar las direcciones de los otros nodos
peers = []

# Función para crear un socket UDP con el flag SO_REUSEPORT
def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", UDP_PORT))
    return sock

# Función para enviar un mensaje UDP a una dirección
def send_message(sock, message, address):
    try:
        sock.sendto(message, address)
        print(f"Mensaje enviado a {address}")
    except OSError as e:
        print(f"Error al enviar mensaje a {address}: {e}")

# Función para escuchar mensajes UDP y responder
def listen(sock):
    while True:
        try:
            data, address = sock.recvfrom(1024)
            print(f"Mensaje recibido de {address}: {data}")
            if data == b"DISCOVER": 
                send_message(sock, b"ACK", address)
            elif data == b"ACK": 
                if address not in peers:
                    peers.append(address)
                    print(f"Pare agregado: {address}")
            else: 
                send_message(sock, data, address)
        except OSError as e:
            print(f"Error al recibir datos: {e}")

# Función para enviar mensajes UDP periódicamente a los pares
def send(sock):
    while True:
        for peer in peers:
            send_message(sock, MESSAGE, peer)
        time.sleep(MESSAGE_INTERVAL)

# Función para descubrir otros nodos usando el servidor de descubrimiento
def discover(sock):
    send_message(sock, b"DISCOVER", DISCOVERY_SERVER)
    while True:
        data, address = sock.recvfrom(1024)
        if data.startswith(b"PEER"):
            peer = data[5:].decode().split(":")
            peer_address = (peer[0], int(peer[1]))
            if peer_address != (socket.gethostbyname(socket.gethostname()), UDP_PORT):
                send_message(sock, b"DISCOVER", peer_address)

# Crear y empezar hilos
def start_threads():
    sock = create_socket()
    listen_thread = threading.Thread(target=listen, args=(sock,))
    send_thread = threading.Thread(target=send, args=(sock,))
    discover_thread = threading.Thread(target=discover, args=(sock,))
    
    listen_thread.daemon = True
    send_thread.daemon = True
    discover_thread.daemon = True
    
    listen_thread.start()
    send_thread.start()
    discover_thread.start()

    listen_thread.join()
    send_thread.join()
    discover_thread.join()

if __name__ == "__main__":
    start_threads()
