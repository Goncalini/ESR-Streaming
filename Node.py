import argparse
import socket
import threading

'''
The application oNode is executed to initialize each node in the network and maintain 
the communication with its neighbouring nodes.
'''

# TODO: Do enunciado falta "Definir estratégia para abandono, se o nó avisa, se deve registar-se periodicamente, etc.."

# TODO: alter message sending mode, currently its user input

def send_message(sock):
    while True:
        message = input()
        sock.sendall(message.encode('utf-8'))


# TODO: alter message receiveing mode, currently its printing

def receive_message(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        message = data.decode('utf-8')
        print(message)


def connect_neighbour(neighbour, port):
    neighbor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        neighbor_sock.connect((neighbour, port))
        print(f"Connected to neighbour {neighbour}:{port}")

        threading.Thread(target=send_message, args=(neighbor_sock,)).start()
        threading.Thread(target=receive_message, args=(neighbor_sock,)).start()

    except Exception as e:
        print(f"Failed to connect to neighbour {neighbour}: {e}")
    

def oNode(node_name, bootstrapper_host, bootstrapper_port):

    # The node connects to the bootsrtapper: sends its name to register
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((bootstrapper_host, bootstrapper_port))
    sock.sendall(node_name.encode('utf-8'))

    # Receives the list of neighbours from the bootstrapper and connects to them
    neighbors_data = sock.recv(1024).decode('utf-8')
    print(f"Vizinhos do {node_name}: {neighbors_data}")

    neighbors = neighbors_data.split(',')
    if neighbors_data != "":
        print(f"{node_name} connecting to neighbours: {neighbors}")
        for n in neighbors:
            connect_neighbour(neighbors.strip())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("node_name", help="Current node's name")
    parser.add_argument("bootstrapper_host", help="Bootstrapper's host")
    parser.add_argument("bootstrapper_port", type=int, help="Bootstrapper's port")
    
    args = parser.parse_args()

    oNode(args.node_name, args.bootstrapper_host, args.bootstrapper_port)
