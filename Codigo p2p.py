#—---------codigo para buscar—-----------------

import socket 
import threading  

class PeerToPeer:
    def __init__(self, port):
        self.ip = '0.0.0.0'  # Escuchar en todas las interfaces disponibles
        self.port = port
        self.peers = []
        self.lock = threading.Lock()
        self.next_peer_port = 9000  # Puerto inicial para asignar a los nuevos clientes

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)
        print(f"Peer escuchando en {self.ip}:{self.port}")

        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            try:
                client_socket, client_address = self.socket.accept()
                print(f"Conexión desde {client_address}")
                self.lock.acquire()
                self.peers.append((client_socket, client_address))
                self.lock.release()
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except Exception as e:
                print(f"Error al aceptar la conexión: {e}")

    def handle_client(self, client_socket, client_address):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Recibido: {data.decode()}")
                self.broadcast_message(data, client_address)
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"Cliente {client_address} desconectado")
        client_socket.close()
        self.lock.acquire()
        self.peers = [(sock, addr) for sock, addr in self.peers if sock != client_socket]
        self.lock.release()
        self.broadcast_message(f"Cliente {client_address} desconectado", client_address)

    def connect_to_peer(self, peer_ip, peer_port):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_ip, peer_port))
            print(f"Conectado a {peer_ip}:{peer_port}")
            self.lock.acquire()
            self.peers.append((peer_socket, (peer_ip, peer_port)))
            self.lock.release()
            threading.Thread(target=self.handle_client, args=(peer_socket, (peer_ip, peer_port))).start()
            return peer_socket
        except Exception as e:
            print(f"Fallo al conectar: {e}")
            return None

    def send_to_peer(self, peer_socket, message):
        try:
            peer_socket.sendall(message.encode())
            print(f"Enviado a peer {peer_socket.getpeername()}: {message}")
        except Exception as e:
            print(f"Fallo al enviar a peer {peer_socket.getpeername()}: {e}")

    def broadcast_message(self, message, sender_address):
        for _, addr in self.peers:
            if addr != sender_address:
                self.send_to_peer(_, message)

    def show_connected_peers(self):
        if not self.peers:
            print("No hay compañeros disponibles.")
            return

        print("Compañeros conectados:")
        for i, (_, address) in enumerate(self.peers):
            print(f"{i}: {address}")
        print(f"{len(self.peers)}: Desconectarse")

    def send_message_to_peer(self):
        if not self.peers:
            print("No hay compañeros disponibles.")
            return

        self.show_connected_peers()

        try:
            peer_index_str = input("Seleccione con qué compañero desea conversar o si desea desconectarse: ").strip()
            peer_index = int(peer_index_str)
            if 0 <= peer_index < len(self.peers):
                peer_socket, _ = self.peers[peer_index]
                while True:
                    message = input("Ingrese el mensaje que desea enviar ('exit' para salir): ")
                    if message.lower() == "exit":
                        break
                    self.send_to_peer(peer_socket, message)
            elif peer_index == len(self.peers):
                print("Desconectándose...")
                exit()
            else:
                print("Índice de compañero no válido")
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un índice válido.")

if __name__ == "__main__":
    peer = PeerToPeer(8888)
    peer.start()
    
    while True:
        peer.send_message_to_peer()
