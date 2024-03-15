# Importa las librerias necesarias para el funcionamiento
import socket
import threading

# Lista para almacenar las direcciones IP de los clientes conectados
connected_clients = []

# Función para manejar las conexiones de los clientes
def handle_client(client_socket, addr):
    print(f"Conexión establecida desde {addr}")
    
    # Agregar la dirección IP del cliente a la lista de clientes conectados
    connected_clients.append(addr)
    
    while True:
        # Recibir datos del cliente
        data = client_socket.recv(1024)
        if not data:
            break
        
        print(f"Mensaje recibido de {addr}: {data.decode('utf-8')}")
        
        # Responder al cliente
        response = input("Responder: ")
        client_socket.send(response.encode('utf-8'))
    
    # Cuando el cliente se desconecta, eliminar su dirección IP de la lista
    connected_clients.remove(addr)
    print(f"Cliente {addr} desconectado.")
    client_socket.close()

# Función para manejar las conexiones de los servidores
def handle_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    
    print(f"Servidor iniciado en {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        
        # Iniciar un hilo para manejar al cliente
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

        # Imprimir la lista de clientes conectados
        print("Clientes conectados:", connected_clients)

# Función para escanear direcciones IP en un rango de puertos y determinar cuáles están disponibles
def scan_ips(start_ip, end_ip):
    available_ips = []
    for ip in range(start_ip, end_ip + 1):
        test_ip = f"{host_prefix}{ip}"
        try:
            socket.create_connection((test_ip, port), timeout=1)
        except socket.error:
            available_ips.append(test_ip)
    return available_ips

# Configuración básica del servidor
host_prefix = '192.168.1.'  # Cambiar según la red local
start_ip = 1
end_ip = 10
port = 9999

# Escanear las direcciones IP disponibles en el rango especificado
available_ips = scan_ips(start_ip, end_ip)
if not available_ips:
    print("No hay direcciones IP disponibles en el rango especificado.")
    exit()

print("Direcciones IP disponibles:")
for ip in available_ips:
    print(ip)

# Solicitar al usuario que ingrese una dirección IP
desired_ip = input("Ingrese la dirección IP deseada: ")
if desired_ip not in available_ips:
    print("La dirección IP ingresada no está disponible.")
    exit()

host = desired_ip

# Iniciar un hilo para manejar conexiones entrantes
server_thread = threading.Thread(target=handle_server)
server_thread.daemon = True
server_thread.start()

# Iniciar el cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

while True:
    # Enviar mensaje al servidor
    message = input("Mensaje para el servidor: ")
    client.send(message.encode('utf-8'))
    
    # Recibir respuesta del servidor
    response = client.recv(1024)
    print("Respuesta del servidor:", response.decode('utf-8'))
