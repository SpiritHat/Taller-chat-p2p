import socket  # Importa el módulo 'socket' para la comunicación de red
import threading  # Importa el módulo 'threading' para manejar múltiples hilos de ejecución

class Client:  # Define la clase 'Client' para manejar la lógica del cliente
    def __init__(self, port):  # Método constructor de la clase 'Client' con un puerto como parámetro
        self.port = port  # Asigna el puerto pasado como argumento a la instancia del cliente
        self.connected_clients = []  # Inicializa una lista para almacenar clientes conectados
        self.server_socket = None  # Inicializa el socket del servidor como vacío
        self.shutdown_flag = False  # Bandera para indicar si el servidor debe apagarse
        self.server_thread = None  # Inicializa el hilo del servidor como vacío

    def start(self):  # Método para iniciar el cliente
        self.server_thread = threading.Thread(target=self.start_server)  # Crea un hilo para ejecutar el servidor
        self.server_thread.start()  # Inicia el hilo del servidor
        self.show_available_clients()  # Muestra los clientes disponibles en la red

    def start_server(self):  # Método para iniciar el servidor
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea el socket del servidor
            self.server_socket.bind(("192.168.2.139", self.port))  # Asocia el socket a una dirección IP y puerto específicos
            self.server_socket.listen(5)  # Pone el socket en modo de escucha para aceptar conexiones entrantes
            print(f"Servidor escuchando en el puerto {self.port}")  # Imprime un mensaje indicando que el servidor está escuchando

            while not self.shutdown_flag:  # Bucle para aceptar conexiones mientras la bandera de apagado esté en False
                client_socket, client_address = self.server_socket.accept()  # Acepta una conexión entrante
                print(f"Conexión entrante desde {client_address}")  # Imprime la dirección del cliente conectado
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()  # Crea un hilo para manejar al cliente conectado
        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")  # Maneja errores al iniciar el servidor

    def handle_client(self, client_socket):  # Método para manejar la conexión con un cliente
        client_ip = client_socket.getpeername()[0]  # Obtiene la dirección IP del cliente
        print(f"Conexión establecida con el cliente en {client_ip}")  # Imprime un mensaje indicando la conexión establecida
        self.connected_clients.append((client_ip, client_socket))  # Agrega el cliente a la lista de clientes conectados

        while True:  # Bucle para recibir mensajes del cliente
            try:
                message = client_socket.recv(1024).decode()  # Recibe mensajes del cliente
                if message.lower() == 'exit':  # Si el mensaje es 'exit', termina el bucle
                    break
                else:
                    print(f"Mensaje recibido de {client_ip}: {message}")  # Imprime el mensaje recibido del cliente
            except Exception as e:
                print(f"Error al recibir mensaje del cliente {client_ip}: {e}")  # Maneja errores al recibir mensajes
                break

    def show_available_clients(self):  # Método para mostrar los clientes disponibles en la red
        while not self.shutdown_flag:  # Bucle para buscar clientes disponibles mientras la bandera de apagado esté en False
            print("Buscando clientes disponibles en la red...")  # Imprime un mensaje indicando la búsqueda de clientes
            available_clients = []  # Inicializa una lista para almacenar clientes disponibles

            for i in range(135, 142):  # Bucle para iterar sobre las direcciones IP en una gama específica
                ip = f"192.168.2.{i}"  # Construye la dirección IP a partir del rango especificado
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket de cliente
                    client_socket.settimeout(0.5)  # Establece un tiempo de espera para la conexión
                    client_socket.connect((ip, self.port))  # Intenta conectar con el cliente en la dirección IP actual
                    print(f"Cliente disponible: {ip}")  # Imprime un mensaje indicando que el cliente está disponible
                    available_clients.append((ip, client_socket))  # Agrega el cliente disponible a la lista
                except Exception as e:
                    pass  # Ignora errores de conexión y continúa con la siguiente dirección IP

            if available_clients:  # Si se encontraron clientes disponibles
                print("Clientes disponibles:")  # Imprime un mensaje indicando que se encontraron clientes disponibles
                for idx, (ip, _) in enumerate(available_clients, start=1):  # Itera sobre los clientes disponibles enumerándolos
                    print(f"{idx}. {ip}")  # Imprime la dirección IP del cliente disponible

                while True:  # Bucle para permitir al usuario elegir un cliente para conectarse
                    try:
                        choice = int(input("Ingrese el número del cliente al que desea conectarse: "))  # Solicita al usuario que elija un cliente
                        chosen_ip, chosen_socket = available_clients[choice - 1]  # Obtiene la dirección IP y el socket del cliente elegido
                        if chosen_ip in [client[0] for client in self.connected_clients]:  # Verifica si ya está conectado a ese cliente
                            response = input("Ya está conectado a este cliente. ¿Desea conectar otro? (s/n): ")  # Solicita al usuario que confirme si desea conectarse a otro cliente
                            if response.lower() == 's':  # Si el usuario desea conectarse a otro cliente, sale del bucle
                                break
                            else:
                                self.show_connected_clients()  # Muestra los clientes conectados y sale del método
                                return
                        else:
                            print(f"Conectando al cliente en {chosen_ip}")  # Imprime un mensaje indicando que se está conectando al cliente
                            self.connect_to_client(chosen_ip, chosen_socket)  # Conecta al cliente elegido
                            break  # Sale del bucle después de conectarse al cliente
                    except (ValueError, IndexError):  # Maneja errores de entrada inválida del usuario
                        print("Opción inválida.")  # Imprime un mensaje indicando que la opción ingresada es inválida

            else:  # Si no se encontraron clientes disponibles
                print("No se encontraron clientes disponibles en la red.")  # Imprime un mensaje indicando que no se encontraron clientes disponibles
                break  # Sale del bucle después de buscar clientes disponibles

        self.show_connected_clients()  # Muestra los clientes conectados

    def connect_to_client(self, ip, client_socket):  # Método para conectar a un cliente
        try:
            print(f"Conexión establecida con el cliente en {ip}")  # Imprime un mensaje indicando la conexión establecida
            self.connected_clients.append((ip, client_socket))  # Agrega el cliente conectado a la lista de clientes conectados
        except Exception as e:
            print(f"Error al conectarse al cliente: {e}")  # Maneja errores al conectarse al cliente

    def show_connected_clients(self):  # Método para mostrar los clientes conectados
        print("Clientes conectados:")  # Imprime un mensaje indicando que se mostrarán los clientes conectados
        for idx, (ip, _) in enumerate(self.connected_clients, start=1):  # Itera sobre los clientes conectados enumerándolos
            print(f"{idx}. {ip}")  # Imprime la dirección IP del cliente conectado
        print("0. Desconectar servidor")  # Imprime una opción para desconectar el servidor

        while True:  # Bucle para permitir al usuario elegir un cliente con el que hablar
            try:
                choice = int(input("Con qué cliente desea hablar (ingrese el número) o '0' para salir: "))  # Solicita al usuario que elija un cliente o una opción para salir
                if choice == 0:  # Si el usuario elige salir
                    self.shutdown_server()  # Apaga el servidor y sale del método
                    return
                elif 1 <= choice <= len(self.connected_clients):  # Si el usuario elige hablar con un cliente
                    client_ip, client_socket = self.connected_clients[choice - 1]  # Obtiene la dirección IP y el socket del cliente elegido
                    print(f"Conversando con {client_ip}")  # Imprime un mensaje indicando que está conversando con el cliente
                    self.send_message(client_socket)  # Envía un mensaje al cliente elegido
                    break  # Sale del bucle después de enviar el mensaje
                else:  # Si el usuario ingresa una opción inválida
                    print("Opción inválida.")  # Imprime un mensaje indicando que la opción ingresada es inválida
            except ValueError:  # Maneja errores de entrada inválida del usuario
                print("Opción inválida.")  # Imprime un mensaje indicando que la opción ingresada es inválida

    def send_message(self, client_socket):  # Método para enviar mensajes a un cliente
        while True:  # Bucle para permitir al usuario enviar mensajes al cliente
            message = input("Ingrese el mensaje que desea enviar (escriba 'exit' para salir): ")  # Solicita al usuario que ingrese un mensaje
            if message.lower() == 'exit':  # Si el mensaje es 'exit'
                client_socket.sendall(message.encode())  # Envía el mensaje 'exit' al cliente
                break  # Sale del bucle después de enviar 'exit'
            else:  # Si el mensaje no es 'exit'
                client_socket.sendall(message.encode())  # Envía el mensaje al cliente

    def shutdown_server(self):  # Método para apagar el servidor
        print("Apagando el servidor...")  # Imprime un mensaje indicando que se está apagando el servidor
        self.shutdown_flag = True  # Establece la bandera de apagado en True
        if self.server_socket:  # Si el socket del servidor existe
            self.server_socket.close()  # Cierra el socket del servidor
        for _, client_socket in self.connected_clients:  # Itera sobre los clientes conectados
            try:
                client_socket.close()  # Cierra el socket de cada cliente conectado
            except:
                pass  # Ignora errores al cerrar los sockets
        exit()  # Sale del programa después de apagar el servidor

if __name__ == "__main__":  # Si se ejecuta este script como el programa principal
    client = Client(8888)  # Crea una instancia de la clase Client con el puerto 8888
    client.start()  # Inicia el cliente
