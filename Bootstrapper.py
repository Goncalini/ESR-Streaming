import socket
import threading

'''
The Boostrapper is used register nodes in the network and maintain knowledge of
the network overlay. Its configuration is done using a file named 'config.txt'
'''


def load_configuration():
    neighbours = {}
    with open('config.txt', 'r') as file:
        for line in file:
            node, neighbors = line.strip().split(':')
            neighbors[node] = neighbors.split(',')
    return neighbours


def init_new_node(conn, addr, neighbours):
    # Connect to new node
    node_name = conn.recv(1024).decode('utf-8')
    print(f"New node registered: {addr} {node_name}")
    
    # Send new node its neighbours
    if node_name in neighbours:
        neighbors = ','.join(neighbours[node_name])
        conn.sendall(neighbors.encode('utf-8'))
    else:
        conn.sendall("".encode('utf-8'))
    
    conn.close()


def bootstrapper(host='localhost', port=5001):
    neighbours = load_configuration()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Bootstrapper waiting for new nodes...")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=init_new_node, args=(conn, addr, neighbours)).start()


if __name__ == "__main__":
    bootstrapper()
