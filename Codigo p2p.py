import socket 
import threading  

class PeerToPeer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.peers = []
        self.lock = threading.Lock()

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)
        print(f"Escuchando en {self.ip}:{self.port}")

        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            try:
                client_socket, client_address = self.socket.accept()
                print(f"Conexión desde {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except Exception as e:
                print(f"Error aceptando conexión: {e}")

    def handle_client(self, client_socket, client_address):
        try:
            alias = client_socket.recv(1024).decode().strip()
            print(f"Alias establecido para {client_address}: {alias}")
            self.lock.acquire()
            self.peers.append((client_socket, client_address, alias))
            self.lock.release()
            self.broadcast_message(f"{alias} se ha unido al chat!", sender_address=client_address)

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                mensaje = data.decode().strip()
                print(f"Recibido de {alias}: {mensaje}")
                self.broadcast_message(mensaje, sender_address=client_address)

        except Exception as e:
            print(f"Error manejando cliente {client_address}: {e}")

        finally:
            alias = [peer[2] for peer in self.peers if peer[1] == client_address][0]
            print(f"{alias} se ha desconectado")
            self.lock.acquire()
            self.peers = [(sock, addr, alias) for sock, addr, alias in self.peers if sock != client_socket]
            self.lock.release()
            self.broadcast_message(f"{alias} se ha desconectado")

    def broadcast_message(self, mensaje, sender_address=None):
        for _, addr, alias in self.peers:
            if addr != sender_address:
                self.send_to_peer(_, f"{alias}: {mensaje}")

    def send_to_peer(self, address, mensaje):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect(address)
            peer_socket.sendall(mensaje.encode())
            peer_socket.close()
        except Exception as e:
            print(f"Fallo al enviar mensaje a {address}: {e}")

    def mostrar_clientes_conectados(self):
        if not self.peers:
            print("No hay clientes disponibles.")
            return

        print("Clientes conectados:")
        for i, (_, address, alias) in enumerate(self.peers):
            print(f"{i}: {address} - Alias: {alias}")

    def enviar_mensaje_a_cliente(self):
        if not self.peers:
            print("No hay clientes disponibles.")
            return

        self.mostrar_clientes_conectados()

        try:
            indice_cliente_str = input("Ingrese el índice del cliente al que desea enviar el mensaje: ").strip()
            indice_cliente = int(indice_cliente_str)
            if 0 <= indice_cliente < len(self.peers):
                peer_socket, _, _ = self.peers[indice_cliente]
                while True:
                    mensaje = input("Ingrese el mensaje que desea enviar: ")
                    self.send_to_peer(peer_socket, mensaje)
                    continuar_enviando = input("¿Desea enviar más mensajes? (s/n): ").strip().lower()
                    if continuar_enviando != 's':
                        break
            else:
                print("Índice de cliente no válido")
        except ValueError:
            print("Entrada no válida. Por favor ingrese un índice válido.")

if __name__ == "__main__":
    peer = PeerToPeer("192.168.2.139", 8888)
    peer.start()
    
    peer.connect_to_peer("192.168.2.140", 8889)
    peer.connect_to_peer("192.168.2.138", 8887)
    
    while True:
        peer.enviar_mensaje_a_cliente()
        continuar_enviando = input("¿Desea enviar más mensajes? (s/n): ").strip().lower()
        if continuar_enviando != 's':
            break
