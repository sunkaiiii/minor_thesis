from job_manager import JobManager
import socket
import time
import selectors
from datetime import date, datetime
from threading import Thread
from task_generator import ComputingTask

script_file_recv_port = 5057


class NodeInformation:
    def __init__(self, address: str, available_slots: int, latency: int):
        self.address = address
        self.available_slots = available_slots
        self.latency = latency

    def __str__(self) -> str:
        return 'address:{0}, available_slots:{1}, latency:{2}'.format(self.address, self.available_slots, self.latency)


class ClientNode(Thread):
    def __init__(self, job_manager: JobManager):
        super().__init__()
        self.timer = datetime.now()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.job_manager = job_manager

    def reset_timer(self):
        self.timer = datetime.now()

    def send_task(self, task: ComputingTask, node: NodeInformation):
        worker = self.TaskWorker(task, node)
        worker.start()

    class TaskWorker(Thread):
        def __init__(self, task: ComputingTask, node: NodeInformation):
            super().__init__()
            self.task = task
            self.node = node

        def run(self) -> None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                with open(self.task.script_name, 'rb') as f:
                    s.connect((self.node.address, script_file_recv_port))
                    buffer_size = 2048
                    bytes = f.read(buffer_size)
                    while bytes:
                        s.send(bytes)
                        bytes = f.read(buffer_size)

    def run(self):
        self.client.bind(("", 5055))
        while True:
            data, addr = self.client.recvfrom(1024)
            print("received message: {0} from {1}".format(data, addr))
            address = addr[0]
            port = 5056
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                available_slots = self.job_manager.available_slots()
                timestamp = data.decode()
                result = str(available_slots) + ' ' + str(timestamp)
                s.connect((address, port))
                s.sendall(result.encode())


class ServerNode(Thread):
    def __init__(self, new_node_callback, job_manager:JobManager):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server.settimeout(1)
        self.time = datetime.now()
        self.new_node_callback = new_node_callback
        self.script_receiver = self.ScriptReceiver(job_manager)

    def __send_heart_beat(self):
        self.time = datetime.now()
        message = (str(self.time.timestamp())).encode()
        self.server.sendto(message, ('<broadcast>', 5055))
        print("message sent!")

    def send_heart_beat(self):
        sender = Thread(target=self.__send_heart_beat)
        sender.start()

    def run(self):
        # Start to wait for receiving script files
        self.script_receiver.start()

        self.handler.bind(('0.0.0.0', 5056))
        self.handler.listen()
        while True:
            conn, addr = self.handler.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                time_offset = (datetime.now() - self.time).microseconds
                split_data = data.decode().split(' ')
                available_slots = int(split_data[0])
                timestamp = str(split_data[1])
                address = addr[0]
                if timestamp != str(self.time.timestamp()):
                    continue
                node_information = NodeInformation(address, available_slots, time_offset)
                print(node_information)
                self.new_node_callback(node_information)

    class ScriptReceiver(Thread):
        def __init__(self,job_manager:JobManager):
            super().__init__()
            self.file_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.selector = selectors.DefaultSelector()
            self.connection_map = {}
            self.job_manager = job_manager

        def run(self) -> None:
            self.file_receiver.bind(('0.0.0.0', script_file_recv_port))
            self.file_receiver.listen()
            while True:
                conn, addr = self.file_receiver.accept()
                conn.setblocking(False)
                self.selector.register(conn, selectors.EVENT_READ, self.read_script)
                self.connection_map[conn] = addr

        def read_script(self, conn, mask):
            addr = self.connection_map[conn]
            buffer_size = 2048
            file_name = 'script'+addr[0]+'.py'
            with open(file_name, 'wb') as f:
                data = self.file_receiver.recv(buffer_size)
                while data:
                    f.write(data)
                    data = self.file_receiver.recv(buffer_size)
                conn.close()
                del self.connection_map[conn]
            self.job_manager.add_task(ComputingTask(0,file_name))


class NodeManger:
    def __init__(self, job_manager: JobManager):
        self.client = ClientNode(job_manager)
        self.server = ServerNode(self.on_new_node_coming,job_manager)
        self.job_manager = job_manager
        self.nodes = {}
        self.server.start()
        self.client.start()

    def send_heart_beat(self):
        self.nodes = []
        self.server.send_heart_beat()

    def send_task_to_best_node(self, task: ComputingTask, node: NodeInformation):
        self.client.send_task(task, node)

    def on_new_node_coming(self, node: NodeInformation):
        self.nodes[node.address] = node

    def get_best_node(self, except_nodes=None) -> NodeInformation:
        if except_nodes is None:
            except_nodes = []
        sorted_nodes = sorted(self.nodes.values(), key=lambda x: x.lantecy, reverse=True)
        for node in sorted_nodes:
            if node not in except_nodes:
                return node


if __name__ == '__main__':
    node = NodeManger(JobManager())
    node.send_heart_beat()
    time.sleep(5)
