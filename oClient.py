import os
import socket
import threading
import time
import sys
import json
from tkinter import *
from typing import List



ServerHost = "10.0.0.10"
BootPort = 5000
ClientPort = 5001
NodePort   = 5002
RequestPort = 5003
RtpPort = 5005
MonitorPOP = 5059
MonitorPort = 5069
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
        self.current_best_pop = None
        self.threads : List[threading.Thread] = []


        #socket para comunicação com o servidor e obter Points of Presence
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socket_client.bind((client_ip, ClientPort))
        
        self.socket_stream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_stream.bind((client_ip, NodePort))

        self.socket_monitor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_monitor.bind((client_ip, MonitorPort))

        self.signal = threading.Event()
        self.signal2 = threading.Event()
        self.aux_signal = 0
        self.stop = threading.Event()

        self.lock = threading.Lock()
        self.lock2 = threading.Lock()


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
        print(f"Getting stream {self.current_best_pop}")
        #data = self.send_and_receive(self.socket_stream, self.filename.encode(), "10.0.13.2" , RequestPort)
        data = self.send_and_receive(self.socket_stream, self.filename.encode(), self.current_best_pop, RequestPort)
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

    #def get_best_point(self):
    #    print("AAAAAAAAAAAAAAAAAAAAAAAAAAa")
    #    for point in self.points_of_presence:
    #        threadMonitor = threading.Thread(target=self.medir_latencia, args=(point,))
    #        #latencia = self.medir_latencia(point)
    #        #self.points_of_presence[point] = latencia
    #        #print(f"Latência para {point}: {latencia}")
    #        threadMonitor.start()
    #    
    #    self.signal2.wait()
    #    best_point = min(self.points_of_presence, key=self.points_of_presence.get)
    #    self.current_best_pop = best_point
    #    print(f"Best point of presence: {best_point}")
#
    #    #return best_point
    #

    #def medir_latencia(self,ip):
    #    print("ENTREIIIIIIIIIIIIIIIIIIIII")
    #    #for ip in self.points_of_presence:
    #    try:
    #    # Executar o comando ping (1 pacote)
    #        response = os.popen(f"ping -w 4 -c 1 {ip}").read()
    #        print(response)
    # # Verificar se "time=" está presente na resposta
    #        if "time=" in response:
    #        # Extrair a latência
    #            latencia = response.split("time=")[1].split(" ")[0]
    #            self.points_of_presence[ip] = latencia
    #            print(f"Latência para {ip}: {latencia}")
    #            #return float(latencia)
    #        else:
    #            self.points_of_presence[ip] = float('inf')
    #        #return float('inf')  # Latência infinita se não houver resposta
    #    except Exception as e:
    #        self.points_of_presence[ip] = float('inf')
    #        print(f"Erro ao medir a latência de {ip}: {e}")
#
    #    with self.lock2:
    #        self.aux_signal += 1
#
    #    if self.aux_signal == len(self.points_of_presence):
    #        self.signal2.set()
    #        self.aux_signal = 0
    #    #return float('inf')


    #def get_best_point(self):
    #    print("AAAAAAAAAAAAAAAAAAAAAAAAAAa")
    #    for point in self.points_of_presence:
    #        threadMonitor = threading.Thread(target=self.medir_latencia, args=(point,))
    #        #latencia = self.medir_latencia(point)
    #        #self.points_of_presence[point] = latencia
    #        #print(f"Latência para {point}: {latencia}")
    #        threadMonitor.start()
    #    
    #    self.signal2.wait()
    #    best_point = min(self.points_of_presence, key=self.points_of_presence.get)
    #    self.current_best_pop = best_point
    #    print(f"Best point of presence: {best_point}")
#
    #    return best_point

    def medir_latencia(self, node_ip):
        print("Medindo Latencia")
        #for node_ip in self.points_of_presence:
        ##try:
        timestamp = time.time()
        #print("1")
        #print(node_ip)
        resp = self.send_and_receive(self.socket_monitor, b'', node_ip, MonitorPort)
        #print("2")
        if resp is None:
            #print("3")
            self.points_of_presence[node_ip] = float('inf')
            #if self.current_best_pop == node_ip:
            #    print(f"Node {node_ip} went down")
            #    self.get_best_point()

        else:
            #print("4")
            timestamp2 = time.time()
            latencia = timestamp2 - timestamp
            #print("5")
            self.points_of_presence[node_ip] = latencia
            print(f"Latência para {node_ip}: {latencia}")
        
        if self.current_best_pop == None:
            self.current_best_pop = node_ip
        elif self.current_best_pop != node_ip:
            if self.points_of_presence[node_ip] < self.points_of_presence[self.current_best_pop]:
                print("redirecionando stream")
                self.interrupt_stream(self.current_best_pop)
                with self.lock:
                    self.current_best_pop = node_ip
                    print(f"End Best point of presence: {self.current_best_pop}")
                self.get_stream()

                
        ##except Exception as e:
            ##    self.points_of_presence[node_ip] = float('inf')
            ##    print(f"Erro ao medir a latência de {node_ip}: {e}")        
                
        ##with self.lock2:
        ##    self.aux_signal += 1
##
        ##if self.aux_signal == len(self.points_of_presence):
        ##    self.signal2.set()
        ##    self.aux_signal = 0
        #return float('inf')
    
    def interrupt_stream(self, point):
        print("INTERRUPTING STREAM")
        socket_pop = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_pop.bind((self.client_host, MonitorPOP))

        socket_pop.sendto(b'', (point, MonitorPOP))


    ##def update_pop(self):
    ##    old_pop = self.current_best_pop
    ##    new_pop = self.get_best_point()
    ##    if old_pop != new_pop:
    ##        print(f"New Best PoP found {new_pop}")
    ##        self.interrupt_stream(old_pop)
    ##        with self.lock:
    ##            self.current_best_pop = new_pop
    ##        self.get_stream()

        #latencia = self.medir_latencia(point)
        #self.points_of_presence[point] = latencia
        #print(f"Latência para {point}: {latencia}")
#
        #if point == self.current_best_pop:
        #    best_point = min(self.points_of_presence, key=self.points_of_presence.get)
        #    if best_point != self.current_best_pop:
        #        print(f"Best point of presence: {best_point}")
        #        self.current_best_pop = best_point
        #        self.get_stream()
        #        self.createStream()


    def start_monitoring(self, point):
        while self.running:
            print(f"Current best point of presence: {self.current_best_pop}")
            print(f"Checking latency: {point}")
            self.medir_latencia(point)
            time.sleep(5)
        
    def monitor_point_of_presence(self):
        for point in self.points_of_presence.keys():     
            monitor_thread = threading.Thread(target=self.start_monitoring, args=(point,))
            monitor_thread.start()
            self.threads.append(monitor_thread)

    def first_check_pop(self):
        threads = []
        for point in self.points_of_presence.keys():
            threads.append(threading.Thread(target=self.medir_latencia, args=(point,)))
        for thread in threads:
             thread.start()
             
        for thread in threads:
            thread.join()

            
        if self.current_best_pop == None:
            print("Error: Could not find a point of presence")
            sys.exit(1)

        else: 
            print(f"IIIIIII Best point of presence: {self.current_best_pop}")
    

    def run(self):
        client_thread = threading.Thread(target=self.connect_server)
        client_thread.start()

        self.signal.wait()

        client.first_check_pop()
        #client.get_best_point()
        client.get_stream()

        client.monitor_point_of_presence()

        client.createStream()

        try:
            while self.running:
                pass
        except KeyboardInterrupt:
            print("Shutting down the client.")
            self.running = False
            ClientWorker.closeStream()
            client_thread.join()
            for thread in self.threads:
                thread.join()
            
            #close all socket
            self.socket_client.close()
            self.socket_stream.close()
            self.socket_monitor.close()
            self.stop.set()
            
            

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












    