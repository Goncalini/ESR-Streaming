import socket
import threading
import sys
import time
from VideoStream import VideoStream
from RtpPacket import RtpPacket

class ServerWorker:
    def __init__(self, stream_path, streamPort):
        self.oNode_requesting = None
        self.stream_path = stream_path
        self.streamPort = streamPort

        self.videoStream = VideoStream(stream_path)

        self.closeStream = threading.Event()
    


        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp_socket.bind(('', streamPort))
    
    def update_oNode_requesting(self, oNode_requesting):
        self.oNode_requesting = oNode_requesting

    def sendRtp(self):
        while not self.closeStream.is_set():
            frame = self.videoStream.nextFrame()
            if frame:
                frameNbr = self.videoStream.frameNbr()
                try:
                    #print(f"Sending frame {frameNbr}")
                    #print(f"oNode_Ip: {self.oNode_requesting}")
                    self.rtp_socket.sendto(self.makeRtp(frame, frameNbr), (self.oNode_requesting, self.streamPort))
                except Exception as e:
                    #print(f"Error sending frame: {e}")
                    pass
            time.sleep(0.05)
    
    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26 # MJPEG type
        seqnum = frameNbr
        ssrc = 0 
        
        rtpPacket = RtpPacket()
        
        rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
        
        return rtpPacket.getPacket()
    
    def close(self):
        #self.videoStream.release() ?????-> Nao sei se é necessario
        self.closeStream.set()
        self.rtp_socket.close()
        
        print("Stream closed")