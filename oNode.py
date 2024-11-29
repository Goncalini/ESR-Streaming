import socket
import threading
import sys

bootstrapper_host = "10.0.0.10"
bootstrapper_port = 5000

NodePort = 5002
RequestPort = 5003


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

        except Exception as e:
            print(f"Error connecting to bootstrapper: {e}")
    
    def get_parent_from_bootstrapper(self):
        try:
            self.parent = self.bootstrapper_socket.recv(1024).decode()
            print("Parent: " + self.parent)
        except Exception as e:
            print(f"Error receiving parent from bootstrapper: {e}")

    def redirect_stream(self, rtp_socket, stream_name):
        #rtp_socket.settimeout(1)
        while not self.stoprog.is_set():
            try:
                data, address = rtp_socket.recvfrom(40480)
                print(f"Received data from {address}")
                stream = self.stream_dick.get(stream_name)
                for nod in stream["nodes_interested"]:
                    rtp_socket.sendto(data, (nod, stream("port")))
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
            print("ola")
        else:
            if self.parent is not None:
                print("pika")
                response_enconded = self.send_and_receive(self.socket_stream, video.encode(), self.parent, NodePort)
                print("ola2")
                if response_enconded is None:
                    print("No responses from parent")
                    return
                
                rtpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                rtpsocket.bind(self.node_id, stream["port"])

                stream["thread"] = threading.Thread(target=self.redirect_stream, args=(rtpsocket, video))
                stream["thread"].start()
                stream["running"] = True
                stream["nodes_interested"].add(address)
                self.stream_dick[video] = stream

    def receive_request(self):
        #self.socket_request.settimeout(1)
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
        print("1")
        socket.sendto(message, (ip, port))
        print("2")
        socket.settimeout(timeout)
        print("3")
        for _ in range(retries):
            try:
                print("4")
                data, _ = socket.recvfrom(1024)
                print("5")
                return data
            except socket.timeout:
                print("6")
                socket.sendto(message, (ip, port))
        print("7")
        return None
    
    def run(self):
        self.connect_to_bootstrapper()
        self.get_parent_from_bootstrapper()
        self.thread_stream.start()
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