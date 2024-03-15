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
        print(f"Peer listening on {self.ip}:{self.port}")

        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            try:
                client_socket, client_address = self.socket.accept()
                print(f"Connection from {client_address}")
                self.lock.acquire()
                self.peers.append((client_socket, client_address))
                self.lock.release()
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_client(self, client_socket, client_address):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
                self.broadcast_message(data, client_address)
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"Client {client_address} disconnected")
        client_socket.close()
        self.lock.acquire()
        self.peers = [(sock, addr) for sock, addr in self.peers if sock != client_socket]
        self.lock.release()
        self.broadcast_message(f"Client {client_address} disconnected", client_address)

    def connect_to_peer(self, peer_ip, peer_port):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_ip, peer_port))
            print(f"Connected to {peer_ip}:{peer_port}")
            self.lock.acquire()
            self.peers.append((peer_socket, (peer_ip, peer_port)))
            self.lock.release()
            threading.Thread(target=self.handle_client, args=(peer_socket, (peer_ip, peer_port))).start()
            return peer_socket
        except Exception as e:
            print(f"Connection failed: {e}")
            return None

    def send_to_peer(self, peer_socket, message):
        try:
            peer_socket.sendall(message.encode())
            print(f"Sent to peer {peer_socket.getpeername()}: {message}")
        except Exception as e:
            print(f"Failed to send to peer {peer_socket.getpeername()}: {e}")

    def broadcast_message(self, message, sender_address):
        for _, addr in self.peers:
            if addr != sender_address:
                self.send_to_peer(_, message)

    def show_connected_peers(self):
        if not self.peers:
            print("No peers available.")
            return

        print("Connected peers:")
        for i, (_, address) in enumerate(self.peers):
            print(f"{i}: {address}")

    def send_message_to_peer(self):
        if not self.peers:
            print("No peers available.")
            return

        self.show_connected_peers()

        try:
            peer_index_str = input("Enter the index of the peer you want to send the message to: ").strip()
            peer_index = int(peer_index_str)
            if 0 <= peer_index < len(self.peers):
                peer_socket, _ = self.peers[peer_index]
                while True:
                    message = input("Enter the message you want to send: ")
                    self.send_to_peer(peer_socket, message)
                    continue_sending = input("Do you want to send more messages? (y/n): ").strip().lower()
                    if continue_sending != 'y':
                        break
            else:
                print("Invalid peer index")
        except ValueError:
            print("Invalid input. Please enter a valid index.")

if __name__ == "__main__":
    peer = PeerToPeer("192.168.2.139", 8888)
    peer.start()
    
    peer.connect_to_peer("192.168.2.140", 8889)
    peer.connect_to_peer("192.168.2.141", 8890)
    
    while True:
        peer.send_message_to_peer()
        continue_sending = input("Do you want to send more messages? (y/n): ").strip().lower()
        if continue_sending != 'y':
            break
