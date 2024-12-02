import os
import socket
import threading
import time
import sys
import json
from tkinter import *


ServerHost = "10.0.0.10"
BootPort = 5000
ClientPort = 5001
NodePort   = 5002
RequestPort = 5003
RtpPort = 5005
from ClientWorker import ClientWorker


class Client:
    def __init__(self, client_name, client_ip, filename):
        self.server_host = ServerHost
        self.rtp_port = RtpPort
        self.client_name = client_name
        self.client_host = client_ip
        self.filename = filename
        self.points_of_presence = {}
        self.running = True
        self.root = Tk()
        #socket para comunicação com o servidor e obter Points of Presence
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socket_client.bind((client_ip, ClientPort))
        
        self.socket_stream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_stream.bind((client_ip, NodePort))

        self.signal = threading.Event()

    def createStream(self):
        ClientWorker(self.root, self.filename)
        self.root.mainloop()

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

            self.signal.set()

        except Exception as e:
            print(f"Error connecting to server: {e}")

    def get_stream(self):
        print("PILAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEEEEEEEEEEEEEE")
        #data = self.send_and_receive(self.socket_stream, self.filename.encode(), "10.0.13.2" , RequestPort)
        data = self.send_and_receive(self.socket_stream, self.filename.encode(), self.get_best_point(), RequestPort)
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

        self.signal.wait()

        client.get_stream()
        client.createStream()


        try:
            while self.running:
                pass
        except KeyboardInterrupt:
            print("Shutting down the client.")
            self.running = False
            client_thread.join()

    def get_best_point(self):
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAa")
        for point in self.points_of_presence:
            latencia = self.medir_latencia(point)
            self.points_of_presence[point] = latencia
            print(f"Latência para {point}: {latencia}")

        best_point = min(self.points_of_presence, key=self.points_of_presence.get)
        print(f"Best point of presence: {best_point}")

        return best_point
    

    def medir_latencia(self, ip):
        print("ENTREIIIIIIIIIIIIIIIIIIIII")
        try:
        # Executar o comando ping (1 pacote)
            response = os.popen(f"ping -c 1 {ip}").read()
            print(response)

        # Verificar se "time=" está presente na resposta
            if "time=" in response:
            # Extrair a latência
                latencia = response.split("time=")[1].split(" ")[0]
                return float(latencia)

            return float('inf')  # Latência infinita se não houver resposta
        except Exception as e:
            print(f"Erro ao medir a latência de {ip}: {e}")
        return float('inf')

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












    