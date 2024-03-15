import socket
import threading

class Client:
    def __init__(self, port):
        self.port = port
        self.connected_clients = []
        self.server_socket = None
        self.shutdown_flag = False
        self.server_thread = None

    def start(self):
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()
        self.show_available_clients()

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("192.168.2.140", self.port))
            self.server_socket.listen(5)
            print(f"Servidor escuchando en el puerto {self.port}")

            while not self.shutdown_flag:
                client_socket, client_address = self.server_socket.accept()
                print(f"Conexión entrante desde {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")

    def handle_client(self, client_socket):
        client_ip = client_socket.getpeername()[0]
        print(f"Conexión establecida con el cliente en {client_ip}")
        self.connected_clients.append((client_ip, client_socket))

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message.lower() == 'exit':
                    break
                else:
                    print(f"Mensaje recibido de {client_ip}: {message}")
            except Exception as e:
                print(f"Error al recibir mensaje del cliente {client_ip}: {e}")
                break

    def show_available_clients(self):
        while not self.shutdown_flag:
            print("Buscando clientes disponibles en la red...")
            available_clients = []
            for i in range(135, 142):
                ip = f"192.168.2.{i}"
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.settimeout(0.5)
                    client_socket.connect((ip, self.port))
                    print(f"Cliente disponible: {ip}")
                    available_clients.append((ip, client_socket))
                except Exception as e:
                    pass

            if available_clients:
                print("Clientes disponibles:")
                for idx, (ip, _) in enumerate(available_clients, start=1):
                    print(f"{idx}. {ip}")

                while True:
                    try:
                        choice = int(input("Ingrese el número del cliente al que desea conectarse: "))
                        chosen_ip, chosen_socket = available_clients[choice - 1]
                        if chosen_ip in [client[0] for client in self.connected_clients]:
                            response = input("Ya está conectado a este cliente. ¿Desea conectar otro? (s/n): ")
                            if response.lower() == 's':
                                break
                            else:
                                self.show_connected_clients()
                                return
                        else:
                            print(f"Conectando al cliente en {chosen_ip}")
                            self.connect_to_client(chosen_ip, chosen_socket)
                            break
                    except (ValueError, IndexError):
                        print("Opción inválida.")

            else:
                print("No se encontraron clientes disponibles en la red.")
                break

        self.show_connected_clients()
    
    def connect_to_client(self, ip, client_socket):
        try:
            print(f"Conexión establecida con el cliente en {ip}")
            self.connected_clients.append((ip, client_socket))
        except Exception as e:
            print(f"Error al conectarse al cliente: {e}")

    def show_connected_clients(self):
        print("Clientes conectados:")
        for idx, (ip, _) in enumerate(self.connected_clients, start=1):
            print(f"{idx}. {ip}")
        print("0. Desconectar servidor")

        while True:
            try:
                choice = int(input("Con qué cliente desea hablar (ingrese el número) o '0' para salir: "))
                if choice == 0:
                    self.shutdown_server()
                    return
                elif 1 <= choice <= len(self.connected_clients):
                    client_ip, client_socket = self.connected_clients[choice - 1]
                    print(f"Conversando con {client_ip}")
                    self.send_message(client_socket)
                    break
                else:
                    print("Opción inválida.")
            except ValueError:
                print("Opción inválida.")

    def send_message(self, client_socket):
        while True:
            message = input("Ingrese el mensaje que desea enviar (escriba 'exit' para salir): ")
            if message.lower() == 'exit':
                client_socket.sendall(message.encode())
                break
            else:
                client_socket.sendall(message.encode())

    def shutdown_server(self):
        print("Apagando el servidor...")
        self.shutdown_flag = True
        if self.server_socket:
            self.server_socket.close()
        for _, client_socket in self.connected_clients:
            try:
                client_socket.close()
            except:
                pass
        exit()


if __name__ == "__main__":
    client = Client(8888)
    client.start()
