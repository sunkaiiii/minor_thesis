from job_manager import JobManager
import socket
import time
from datetime import date, datetime
from threading import Thread



class ClientNode(Thread):
    def __init__(self,job_manager:JobManager):
        super().__init__()
        self.callback = callback
        self.timer = datetime.now()
        self.client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        self.client.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.client.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        self.job_manager = job_manager
        
    def reset_timer(self):
        self.timer = datetime.now()

    def run(self):
        self.client.bind(("",5055))
        while True:
            data,addr = self.client.recvfrom(1024)
            time_offset = (datetime.now()-self.timer).microseconds
            print("received message: {0} from {1}".format(data,addr))
            address = addr[0]
            port = 5056
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                available_slots = self.job_manager.available_slots()
                timestamp = data.decode()
                result = str(available_slots) + ' ' + str(timestamp)
                s.connect((address,port))
                s.sendall(result.encode())

class ServerNode(Thread):
    def __init__(self, new_node_callback):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.handler = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server.settimeout(1)
        self.time = datetime.now()
        self.new_node_callback = new_node_callback
    
    def __send_heart_beat(self):
        self.time = datetime.now()
        message = (str(self.time.timestamp())).encode()
        self.server.sendto(message, ('<broadcast>', 5055))
        print("message sent!")

    def send_heart_beat(self):
        sender = Thread(target=self.__send_heart_beat)
        sender.start()
    
    def run(self):
        self.handler.bind(('0.0.0.0',5056))
        self.handler.listen()
        while True:
            conn,addr = self.handler.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                time_offset = (datetime.now() - self.time).microseconds
                splited_data = data.decode().split(' ')
                available_slots = int(splited_data[0])
                timestamp = str(splited_data[1])
                address = addr[0]
                if timestamp != str(self.time.timestamp()):
                    continue
                node_information = NodeInformation(address,available_slots,time_offset)
                print(node_information)
                self.new_node_callback(node_information)

    
class NodeInformation:
    def __init__(self, address:str, available_slots:int, latency:int):
        self.address = address
        self.available_slots = available_slots
        self.latency = latency 
    
    def __str__(self) -> str:
        return 'address:{0}, available_slots:{1}, latency:{2}'.format(self.address,self.available_slots,self.latency)


class NodeManger:
    def __init__(self, job_manager:JobManager):
        self.client = ClientNode(job_manager)
        self.server = ServerNode(self.on_new_node_coming)
        self.job_manager = job_manager
        self.nodes = []
        self.server.start()
        self.client.start()
    
    def send_heart_beat(self):
        self.nodes = []
        self.server.send_heart_beat()
    
    def on_new_node_coming(self, node:NodeInformation):
        self.nodes.append(node)

if __name__ == '__main__':
    node = NodeManger(JobManager())
    node.send_heart_beat()
    time.sleep(5)