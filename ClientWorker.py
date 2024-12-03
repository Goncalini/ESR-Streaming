
#import socket
#import threading
#from PIL import Image, ImageTk
#import sys, traceback, os
#from tkinter import *
from RtpPacket import RtpPacket
#import time
import socket, threading
from tkinter import *
from PIL import Image, ImageTk
#from ..utils.config import RTP_PORT, SERVER_IP, VIDEO_FILES
#from ..utils.stream.RtpPacket import RtpPacket
import time

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

RtpPort = 5005
ServerHost = "10.0.0.10"
BootPort = 5000
ClientPort = 5001
#NodePort = 5002

Streams_List = {'videos/video_BrskEdu.mp4': 7070, 'videos/movie.Mjpeg': 7072}

class ClientWorker:
    def __init__(self, master, stream_name):
        
        self.master = master
        #self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.master.title("RTP Client")
        self.stream_name = stream_name
        self.server_host = ServerHost
        #self.rtp_port = RtpPort
        self.rtp_port = Streams_List[stream_name]

        self.frameNbr = 0
        self.timestamp = str(int(time.time() * 1000)) #evitar q o nome seja o mesmo para todos os clientes e nao escreverem todos no mesmo ficheiro uns por cima dos outros

        self.rtp_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp_stream_socket.bind(('', self.rtp_port))

        self.end_stream = threading.Event()
        self.thread = threading.Thread(target=self.receiveRtp)

        self.createWidgets()

    def createWidgets(self):
        """Build GUI."""
        self.playButton = Button(self.master, width=20, padx=3, pady=3)
        self.playButton["text"] = "Play"
        self.playButton["command"] = self.startRtpThread
        self.playButton.grid(row=1, column=0, padx=2, pady=2)

        self.closeButton = Button(self.master, width=20, padx=3, pady=3)
        self.closeButton["text"] = "Close"
        self.closeButton["command"] = self.closeStream
        self.closeButton.grid(row=1, column=1, padx=2, pady=2)

        self.label: Label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=2, sticky=W+E+N+S, padx=5, pady=5)


    def startRtpThread(self):
        self.thread.start()


    def closeStream(self):
        self.master.destroy()
        self.rtp_stream_socket.close()
        self.end_stream.set()
        self.thread.join()

    def receiveRtp(self):
        while not self.end_stream.is_set():
            data = self.rtp_stream_socket.recv(40480)
            if data:
                rtpPacket = RtpPacket()
                rtpPacket.decode(data)

                currFrameNbr = rtpPacket.seqNum()
                print(f"Current Sequence Number: " + str(currFrameNbr))

                if currFrameNbr > self.frameNbr:
                    self.frameNbr = currFrameNbr
                    self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
    
    def updateMovie(self, imageFile):
        if imageFile:
            print(f"Updating movie")
        image = Image.open(imageFile)
        photo = ImageTk.PhotoImage(image)
        
        # Dynamically set the label size to match the image
        self.label.configure(image=photo, height=image.size[1], width=image.size[0]) 
        self.label.image = photo
                
    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + self.timestamp + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()
        
        return cachename

