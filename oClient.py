import socket
import threading
import time
import sys
import json


ServerHost = "10.0.0.10"
BootPort = 5000
ClientPort = 5001
NodePort   = 5002
RequestPort = 5003



class Client:
    def __init__(self, client_name, client_ip, filename):
        self.server_host = ServerHost
        self.client_name = client_name
        self.client_host = client_ip
        self.filename = filename
        self.points_of_presence = {}
        self.running = True
        #socket para comunicação com o servidor e obter Points of Presence
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socket_client.bind((client_ip, ClientPort))
        
        self.socket_stream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_stream.bind((client_ip, NodePort))

    def connect_server(self):
        try:
            self.socket_client.sendto(self.client_name.encode(), (self.server_host, ClientPort))
            print("Client sent")
            #recebe os Points of Presence
            self.points_of_presence_enconded = self.socket_client.recv(1024).decode()
            self.points_of_presence_list =  json.loads(self.points_of_presence_enconded)
            if self.points_of_presence_list is None:
                print("Error: Could not get points of presence")
            for point in self.points_of_presence_list:
                self.points_of_presence[point] = float('inf')
            print(self.points_of_presence)
        except Exception as e:
            print(f"Error connecting to server: {e}")

    def get_stream(self):
        data = self.send_and_receive(self.socket_stream, self.filename.encode(), "10.0.13.2" , RequestPort)
        if data is None:
            print("Error: Could not get stream")
            sys.exit(1)
    
    def send_and_receive(self, socket, message, ip, port, timeout = 2.0 , retries = 3):
        socket.sendto(message, (ip, port))
        socket.settimeout(timeout)
        for _ in range(retries):
            try:
                data, _ = socket.recvfrom(1024)
                return data
            except socket.timeout:
                socket.sendto(message, (ip, port))
        return None


    def run(self):
        client_thread = threading.Thread(target=self.connect_server)
        client_thread.start()

        client.get_stream()

        try:
            while self.running:
                pass
        except KeyboardInterrupt:
            print("Shutting down the client.")
            self.running = False
            client_thread.join()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Falta argumentos")
        sys.exit(1)

    client_ip = sys.argv[2]
    client_name = sys.argv[1]
    filename = sys.argv[3]

    print("Client IP: " + client_ip)
    print("Client Name: " + client_name)
    print("Filename: " + filename)

    client = Client(client_name, client_ip, filename)
    client.run()