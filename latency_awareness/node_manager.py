import socket
import time
from threading import Thread



class ClientNode(Thread):
    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        self.client.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.client.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        
    
    def run(self):
        self.client.bind(("",5055))
        while True:
            data,addr = self.client.recvfrom(1024)
            print("received message: {0} from {1}".format(data,addr))

class ServerNode(Thread):
    def __init__(self):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server.settimeout(1)
    
    def __send_heart_beat(self):
        message = b'nothing to say'
        self.server.sendto(message, ('<broadcast>', 5055))
        print("message sent!")

    def send_heart_beat(self):
        sender = Thread(target=self.__send_heart_beat)
        sender.start()

class NodeManger:
    def __init__(self):
        self.client = ClientNode()
        self.server = ServerNode()
        self.client.start()
    
    def send_heart_beat(self):
        self.server.send_heart_beat()

if __name__ == '__main__':
    node = NodeManger()
    node.send_heart_beat()
    # time.sleep(5)