import socket
import threading
import sys


bootstrapper_host = "10.0.0.10"
bootstrapper_port = 5000

NodePort = 5002
RequestPort = 5003
MonitorPOP = 5059
MonitorPort = 5069


Streams_List = {'videos/video_BrskEdu.mp4': 7070, 'videos/movie.Mjpeg': 7072}

class oNode:

    def __init__(self, bootstrapper_host, bootstrapper_port, node_id, node_ip):
        self.bootstrapper_host = bootstrapper_host
        self.bootstrapper_port = bootstrapper_port
        self.node_id = node_id
        self.node_ip = node_ip
        self.parent = None
        self.stream_dick = {}
        for video, port in Streams_List.items():
            self.stream_dick[video] = {
                "running": False,
                "thread": None,
                "port": port,
                "nodes_interested": set()
            }

        #self.running = True

        self.stoprog = threading.Event()

        self.lock = threading.Lock()

        self.thread_stream = threading.Thread(target=self.receive_request)
        
    
    def connect_to_bootstrapper(self):
        try:
            self.bootstrapper_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.socket_stream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_stream.bind((self.node_ip, NodePort))

            self.socket_request = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_request.bind((self.node_ip, RequestPort))

            self.bootstrapper_socket.connect((self.bootstrapper_host, self.bootstrapper_port))
            self.bootstrapper_socket.sendall(self.node_id.encode())

            self.monitoring_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.monitoring_client.bind((self.node_ip, MonitorPOP))

            self.timestamp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.timestamp_socket.bind((self.node_ip, MonitorPort))


        except Exception as e:
            print(f"Error connecting to bootstrapper: {e}")
    
    def get_parent_from_bootstrapper(self):
        try:
            self.parent = self.bootstrapper_socket.recv(1024).decode()
            print("Parent: " + self.parent)
        except Exception as e:
            print(f"Error receiving parent from bootstrapper: {e}")

    def redirect_stream(self, rtp_socket, stream_name):
        rtp_socket.settimeout(1)
        while not self.stoprog.is_set():
            try:
                data, address = rtp_socket.recvfrom(40480)
                print(f"Received data from {address}")
                stream = self.stream_dick.get(stream_name)
                for nod in stream["nodes_interested"]:
                    rtp_socket.sendto(data, (nod, stream["port"])) #())
            except socket.timeout:
                continue
            except Exception as e:
                print(f"An error occurred 1: {e}")
                break         
    
    def ask_stream(self, video, address):
        stream = self.stream_dick.get(video)

        if stream["running"]:
            stream["nodes_interested"].add(address)
            self.stream_dick[video] = stream
            #print("ola")
        else:
            if self.parent is not None:
                ##print("pika")
                response_enconded = self.send_and_receive(self.socket_stream, video.encode(), self.parent, RequestPort)
                #print("ola2")
                if response_enconded is None:
                    print("No responses from parent")
                    return
                
                rtpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #print("FODA SE")
                rtpsocket.bind((self.node_ip, stream["port"]))
                #print("mimi")
                stream["thread"] = threading.Thread(target=self.redirect_stream, args=(rtpsocket, video))
                ##print("mimi 2")
                stream["thread"].start()
                #print("mimi 3")
                stream["running"] = True
                #print("mimi 4")
                stream["nodes_interested"].add(address)
                #print("mimi 5")
                self.stream_dick[video] = stream

    def receive_request(self):
        self.socket_request.settimeout(1)
        while not self.stoprog.is_set():
            try:
                data, address = self.socket_request.recvfrom(1024)
                print(f"Received request from {address}")
                self.socket_request.sendto(b'', address)
                print(f"Video: {data.decode()}")
                self.ask_stream(data.decode(), address[0])
            except socket.timeout:
                continue
            except Exception as e:
                print(f"An error occurred 2: {e}")
                break
                

        
    def send_and_receive(self, socket, message, ip, port, timeout = 2.0 , retries = 3):
        #print("1")
        socket.sendto(message, (ip, port))
        #print("2")
        socket.settimeout(timeout)
        #print("3")
        for _ in range(retries):
            try:
                #print("4")
                data, _ = socket.recvfrom(1024)
                #print("5")
                return data
            except socket.timeout:
                #print("6")
                socket.sendto(message, (ip, port))
        #print("7")
        return None
    
    def remove_cliente(self, ip):
        with self.lock:
            print("entrei remove")
            for stream in self.stream_dick.values():
                if ip in stream["nodes_interested"]:
                    stream["nodes_interested"].remove(ip)
                    print(f"IP {ip} removido")
                    #self.stream_dick[stream] = stream


    def monitor_pop(self):
        while not self.stoprog.is_set():
            try:
                data, address = self.monitoring_client.recvfrom(1024)
                print(data.decode())
                if data.decode() == "interrupt":
                    self.remove_cliente(address[0])
                    print("removido com sucesso")
                    #print(self.stream_dick["nodes_interested"])
                    continue
                
            except Exception as e:
                print(f"An error occurred eliminating Client 3: {e}")
                break

    def handle_timestamp(self):
        while not self.stoprog.is_set():
            try:
                data, address = self.timestamp_socket.recvfrom(1024)
                self.timestamp_socket.sendto("timestamp".encode(), (address[0], MonitorPort))
            except Exception as e:
                print(f"An error occurred handling timestamp: {e}")
                break
                
    
    def run(self):
        self.connect_to_bootstrapper()
        self.get_parent_from_bootstrapper()
        self.thread_stream.start()
        self.threadMonitorPop = threading.Thread(target=self.monitor_pop)
        self.threadMonitorPop.start()
        self.timestampthread = threading.Thread(target=self.handle_timestamp)
        self.timestampthread.start()
        #while self.running:
        #    pass

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Falta argumentos")
        sys.exit(1)

    node_ip = sys.argv[1]
    node_id = sys.argv[2]

    print("Node IP: " + node_ip)
    print("Node ID: " + node_id)

    node = oNode(bootstrapper_host, bootstrapper_port, node_id, node_ip)
    node.run()