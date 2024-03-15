import socket  # Importa el módulo de socket para la comunicación de red
import threading  # Importa el módulo de threading para manejar múltiples conexiones de forma concurrente

class Client:  # Define la clase Client para representar el servidor
    def __init__(self, port):  # Método constructor de la clase
        self.port = port  # Puerto en el que el servidor escuchará conexiones
        self.connected_clients = []  # Lista para almacenar clientes conectados
        self.server_socket = None  # Socket del servidor
        self.shutdown_flag = False  # Bandera para indicar si el servidor debe apagarse
        self.server_thread = None  # Hilo para ejecutar el servidor

    def start(self):  # Método para iniciar el servidor
        self.server_thread = threading.Thread(target=self.start_server)  # Crea un hilo para iniciar el servidor
        self.server_thread.start()  # Inicia el hilo del servidor
        self.show_available_clients()  # Muestra los clientes disponibles en la red

    def start_server(self):  # Método para iniciar el servidor
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP/IP
            self.server_socket.bind(("192.168.2.138", self.port))  # Enlaza el socket a una dirección y puerto específicos
            self.server_socket.listen(5)  # Habilita el socket para aceptar conexiones
            print(f"Servidor escuchando en el puerto {self.port}")  # Muestra un mensaje indicando que el servidor está escuchando

            while not self.shutdown_flag:  # Bucle para aceptar conexiones de forma continua mientras la bandera de apagado sea False
                client_socket, client_address = self.server_socket.accept()  # Acepta una nueva conexión entrante
                print(f"Conexión entrante desde {client_address}")  # Muestra un mensaje indicando la dirección del cliente
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()  # Crea un hilo para manejar el cliente
        except Exception as e:  # Captura excepciones
            print(f"Error al iniciar el servidor: {e}")  # Muestra un mensaje de error

    def handle_client(self, client_socket):  # Método para manejar a un cliente
        client_ip = client_socket.getpeername()[0]  # Obtiene la dirección IP del cliente
        print(f"Conexión establecida con el cliente en {client_ip}")  # Muestra un mensaje indicando la conexión con el cliente
        self.connected_clients.append((client_ip, client_socket))  # Agrega al cliente a la lista de clientes conectados

        while True:  # Bucle para recibir mensajes del cliente de forma continua
            try:
                message = client_socket.recv(1024).decode()  # Recibe un mensaje del cliente
                if not message:  # Si el mensaje está vacío, indica que la conexión se ha cerrado
                    print(f"La conexión con el cliente en {client_ip} se cerró inesperadamente.")
                    self.connected_clients.remove((client_ip, client_socket))  # Elimina al cliente de la lista de clientes conectados
                    client_socket.close()  # Cierra el socket del cliente
                    break  # Sale del bucle
                else:
                    print(f"Mensaje recibido de {client_ip}: {message}")  # Muestra el mensaje recibido del cliente
                    if message.lower() == 'exit':  # Si el mensaje es 'exit', indica que el cliente quiere cerrar la conexión
                        print(f"El cliente en {client_ip} ha cerrado la conexión.")
                        self.connected_clients.remove((client_ip, client_socket))  # Elimina al cliente de la lista de clientes conectados
                        client_socket.close()  # Cierra el socket del cliente
                        break  # Sale del bucle
            except Exception as e:  # Captura excepciones
                print(f"Error al recibir mensaje del cliente {client_ip}: {e}")  # Muestra un mensaje de error
                break  # Sale del bucle

    def show_available_clients(self):  # Método para mostrar los clientes disponibles en la red
        while not self.shutdown_flag:  # Bucle para buscar clientes disponibles mientras la bandera de apagado sea False
            print("Buscando clientes disponibles en la red...")  # Muestra un mensaje indicando que se están buscando clientes
            available_clients = []  # Lista para almacenar los clientes disponibles

            for i in range(135, 142):  # Recorre las direcciones IP para buscar clientes disponibles
                ip = f"192.168.2.{i}"  # Genera una dirección IP
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP/IP
                    client_socket.settimeout(0.5)  # Establece un tiempo de espera para la conexión
                    client_socket.connect((ip, self.port))  # Intenta conectar al cliente
                    print(f"Cliente disponible: {ip}")  # Muestra un mensaje indicando que el cliente está disponible
                    available_clients.append((ip, client_socket))  # Agrega al cliente a la lista de clientes disponibles
                except Exception as e:  # Captura excepciones
                    pass  # Continúa con el siguiente cliente

            if available_clients:  # Si hay clientes disponibles
                print("Clientes disponibles:")  # Muestra un mensaje indicando que hay clientes disponibles
                for idx, (ip, _) in enumerate(available_clients, start=1):  # Itera sobre los clientes disponibles
                    print(f"{idx}. {ip}")  # Muestra la dirección IP del cliente

                while True:  # Bucle para manejar la elección del usuario
                    try:
                        choice = int(input("Ingrese el número del cliente al que desea conectarse: "))  # Solicita al usuario elegir un cliente
                        chosen_ip, chosen_socket = available_clients[choice - 1]  # Obtiene la dirección IP y el socket del cliente elegido
                        if chosen_ip in [client[0] for client in self.connected_clients]:  # Verifica si el cliente ya está conectado
                            response = input("Ya está conectado a este cliente. ¿Desea conectar otro? (s/n): ")  # Pregunta al usuario si desea elegir otro cliente
                            if response.lower() == 's':  # Si el usuario quiere conectar otro cliente
                                break  # Sale del bucle
                            else:
                                self.show_connected_clients()  # Muestra los clientes conectados
                                return  # Retorna
                        else:
                            print(f"Conectando al cliente en {chosen_ip}")  # Muestra un mensaje indicando la conexión al cliente elegido
                            self.connect_to_client(chosen_ip, chosen_socket)  # Establece la conexión con el cliente elegido
                            break  # Sale del bucle
                    except (ValueError, IndexError):  # Captura excepciones de tipo ValueError e IndexError
                        print("Opción inválida.")  # Muestra un mensaje indicando que la opción es inválida

            else:  # Si no hay clientes disponibles
                print("No se encontraron clientes disponibles en la red.")  # Muestra un mensaje indicando que no se encontraron clientes
                break  # Sale del bucle

        self.show_connected_clients()  # Muestra los clientes conectados

    def connect_to_client(self, ip, client_socket):  # Método para conectar con un cliente
        try:
            print(f"Conexión establecida con el cliente en {ip}")  # Muestra un mensaje indicando la conexión con el cliente
            self.connected_clients.append((ip, client_socket))  # Agrega al cliente a la lista de clientes conectados
        except Exception as e:  # Captura excepciones
            print(f"Error al conectarse al cliente: {e}")  # Muestra un mensaje de error

    def show_connected_clients(self):  # Método para mostrar los clientes conectados
        print("Clientes conectados:")  # Muestra un mensaje indicando que se van a mostrar los clientes conectados
        for idx, (ip, _) in enumerate(self.connected_clients, start=1):  # Itera sobre los clientes conectados
            print(f"{idx}. {ip}")  # Muestra la dirección IP del cliente
        print("0. Desconectar servidor")  # Muestra una opción para desconectar el servidor

        while True:  # Bucle para manejar la elección del usuario
            try:
                choice = int(input("Con qué cliente desea hablar (ingrese el número) o '0' para salir: "))  # Solicita al usuario elegir un cliente o salir
                if choice == 0:  # Si el usuario elige salir
                    self.shutdown_server()  # Apaga el servidor
                    return  # Retorna
                elif 1 <= choice <= len(self.connected_clients):  # Si el usuario elige un cliente válido
                    client_ip, client_socket = self.connected_clients[choice - 1]  # Obtiene la dirección IP y el socket del cliente elegido
                    print(f"Conversando con {client_ip}")  # Muestra un mensaje indicando la conversación con el cliente
                    self.send_message(client_socket)  # Envía un mensaje al cliente
                    break  # Sale del bucle
                else:  # Si el usuario elige una opción inválida
                    print("Opción inválida.")  # Muestra un mensaje indicando que la opción es inválida
            except ValueError:  # Captura excepciones de tipo ValueError
                print("Opción inválida.")  # Muestra un mensaje indicando que la opción es inválida

    def send_message(self, client_socket):  # Método para enviar un mensaje al cliente
        while True:  # Bucle para enviar mensajes al cliente de forma continua
            message = input("Ingrese el mensaje que desea enviar (escriba 'exit' para salir): ")  # Solicita al usuario ingresar un mensaje
            if message.lower() == 'exit':  # Si el mensaje es 'exit', indica que se quiere salir
                client_socket.sendall(message.encode())  # Envia el mensaje al cliente
                break  # Sale del bucle
            else:  # Si el mensaje no es 'exit'
                client_socket.sendall(message.encode())  # Envia el mensaje al cliente

    def shutdown_server(self):  # Método para apagar el servidor
        print("Apagando el servidor...")  # Muestra un mensaje indicando que se está apagando el servidor
        self.shutdown_flag = True  # Establece la bandera de apagado a True
        if self.server_socket:  # Si el socket del servidor existe
            self.server_socket.close()  # Cierra el socket del servidor
        for _, client_socket in self.connected_clients:  # Itera sobre los clientes conectados
            try:
                client_socket.close()  # Cierra los sockets de los clientes
            except:  # Captura excepciones
                pass  # Continúa con el siguiente cliente
        exit()  # Sale del programa

if __name__ == "__main__":  # Verifica si el script se ejecuta como programa principal
    client = Client(8888)  # Crea una instancia de la clase Client con el puerto 8888
    client.start()  # Inicia el servidor
