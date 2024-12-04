import socket
import threading
import sys
import time
import TopologiaUtil
import json
from ServerWorker import ServerWorker
from tkinter import Tk

ServerHost = "10.0.0.10"
BootPort = 5000
ClientPort = 5001
NodePort   = 5002
RequestPort = 5003
ServerPort = 5050
Points_of_Presence = ["10.0.13.2","10.0.12.2","10.0.11.2"]

Streams_List = {'videos/video_BrskEdu.mp4': 7070, 'videos/movie.Mjpeg': 7072}

class Server: 

    def __init__ (self, host, port):
        self.host = ServerHost #0.0.0.0
        self.port = BootPort
        self.nodes_active = {}
        self.nodes = []
        self.clients = []
        self.running = True
        self.videos = {}

        self.streams = {video: ServerWorker(video, port) for video, port in Streams_List.items()}

        self.stoprog = threading.Event()

        
    
    
    def start_server(self):
        try:
            self.server_node_bootstrapper = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_node_bootstrapper.bind((self.host, self.port))


            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.bind((self.host, ClientPort))

            self.server_node_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_node_server.bind((self.host, ServerPort))

            self.server_node_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_node_socket.bind((self.host, RequestPort))

            

            print("Server started")
            
            self.register_nodes()
            
        except Exception as e:
            print(f"Error starting server: {e}")

    def register_nodes(self):
              while self.running:   
                    try:
                        data, address = self.server_node_bootstrapper.recvfrom(1024)
                        print("Data: " + data.decode())
                        self.nodes.append(address)
                        if data.decode() not in self.nodes_active:
                            self.nodes_active[data.decode()] = address
                            print("Node " + data.decode() + " added")
                            #print(self.nodes_active)
                            #ajuda = self.nodes_active.get(data.decode())
                            #print(self.get_ip_from_id(data.decode()))
                            #print(ajuda)      
                            #print("x")                        
                          
                        else:
                            print("Node " + data.decode() + " already exists")
                        #print(self.get_ip_from_id(data.decode()))
                        help = TopologiaUtil.getparent(data.decode())
                        #print(help)
                        helpi = self.get_ip_from_id(help)
                        #print(helpi)
                        self.server_node_bootstrapper.sendto(helpi.encode(), address)
                    except Exception as e:
                        print(f"Error receiving data from client: {e}")
 
    def register_clients(self):
         #self.client_socket.settimeout(1) #impede que o socket fique bloqueado indefinidamente ao esperar por dados, permitindo verificar periodicamente a condição de parada.
         while self.running:
            try:
                data, address = self.client_socket.recvfrom(1024)
                #print("Data: " + data.decode())
                print(f"Connect to Client {data.decode()} in {address}")
                if data.decode() not in self.clients:
                    self.clients.append(data.decode())
                    print("Client " + data.decode() + " added")
                else:
                    print("Client " + data.decode() + " already exists")
                self.client_socket.sendto(json.dumps(Points_of_Presence).encode(), address)
            except Exception as e:
                print(f"Error receiving data from client: {e}")


    def get_request_stream(self):
        #self.server_node_socket.settimeout(1) 
        while not self.stoprog.is_set():
            try:
                data, address = self.server_node_socket.recvfrom(1024)
                video = data.decode()
                print(f"Requesting stream {video} from {address}")
                if video in self.streams:
                    self.server_node_socket.sendto(b'', address)
                    self.streams[video].update_oNode_requesting(address[0])
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error receiving data from client: {e}")
                break

    def get_ip_from_id(self, id):
        #a = self.nodes_active.get(id)
        #print(a)
        #print("b")
        #if a[0] == "Server":
        #    print("a")
        #    return ServerHost
        #else: 
        #    return a[0]
        if id == "Server":
            return ServerHost
        else:
            return self.nodes_active.get(id)[0]
    
    def run(self):
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        #server_thread2 = threading.Thread(target=self.register_nodes, daemon=True)
        server_thread2 = threading.Thread(target=self.register_clients, daemon=True)
        server_thread3 = threading.Thread(target=self.get_request_stream, daemon=True)

        server_thread.start()
        server_thread2.start()
        server_thread3.start()
        #server_thread2.start()

        for stream in self.streams.values():
            stream_thread = threading.Thread(target=stream.sendRtp, daemon=True)
            stream_thread.start()

        try:
            while True:
                pass  # Manter o servidor ativo
        except KeyboardInterrupt:
            print("Shutting down the server.")
            self.running = False
            server_thread.join()
        
        

if __name__ == "__main__":
    server = Server(ServerHost, BootPort)
    server.run()