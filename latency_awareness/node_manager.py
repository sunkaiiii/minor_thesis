from job_manager import JobManager
import socket
import time
import selectors
from datetime import date, datetime
from threading import Thread
from task_generator import ComputingTask
import functools

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
        # self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.job_manager = job_manager
        self.BROAD_CAST_IONFOMRATION = '1'
        self.FINISHED_INFORMATION = '2'
        self.broadcast_receiver_selectors = selectors.DefaultSelector()
        self.finish = False

    def stop_service(self):
        self.client.close()
        self.broadcast_receiver_selectors.close()
        self.finish = True
        print('client closed')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        print('client closed')

    def reset_timer(self):
        self.timer = datetime.now()

    def send_task(self, task: ComputingTask, node: NodeInformation, error_callback=None):
        worker = self.TaskWorker(task, node, error_callback)
        worker.start()

    def send_task_execution_finish(self, task: ComputingTask, addr: str):
        print('start sending result back to ' + addr)
        task_finish_worker = self.TaskFinishWorker(task, addr)
        task_finish_worker.start()
        print('sent finish information')

    class TaskFinishWorker(Thread):
        def __init__(self, task: ComputingTask, addr: str):
            super().__init__()
            self.task = task
            self.addr = addr

        def run(self):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    print('send result back to ' + self.addr)
                    s.connect((self.addr, 5056))
                    data = '2' + ' ' + str(self.task.id) + ' ' + str(datetime.now().timestamp())
                    s.send(data.encode())
            except:
                print("send remote task finished error")

    class TaskWorker(Thread):
        def __init__(self, task: ComputingTask, node: NodeInformation, error_callback=None):
            super().__init__()
            self.task = task
            self.node = node
            self.error_callback = error_callback

        # todo selector write client
        def run(self) -> None:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    with open(self.task.script_name, 'rb') as f:
                        print('starting send task to ' + self.node.address + ' ,open socket...')
                        s.connect((self.node.address, script_file_recv_port))
                        print('scoket open, sending data')
                        task_id_len = 5 - len(str(self.task.id))
                        s.send(str(self.task.id).encode())
                        while task_id_len > 0:
                            s.send(' '.encode())
                            task_id_len -= 1
                        buffer_size = 2048
                        bytes = f.read(buffer_size)
                        while bytes:
                            s.send(bytes)
                            bytes = f.read(buffer_size)
                        print('sending data over, close socket')
            except:
                if self.error_callback is not None:
                    self.error_callback(self.task, self.node)

    def run(self):
        self.client.bind(("", 5055))
        while not self.finish:
            try:
                data, addr = self.client.recvfrom(1024)
                print("received message: {0} from {1}".format(data, addr))
                address = addr[0]
                port = 5056
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    available_slots = self.job_manager.available_slots()
                    timestamp = data.decode()
                    result = self.BROAD_CAST_IONFOMRATION + ' ' + str(available_slots) + ' ' + str(timestamp)
                    s.connect((address, port))
                    s.sendall(result.encode())
            except:
                continue


class ServerNode(Thread):
    def __init__(self, new_node_callback, job_manager: JobManager, on_receive_finished_task_information_callback):
        super().__init__()
        self.data_receive_selector = selectors.DefaultSelector()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server.settimeout(1)
        self.time = datetime.now()
        self.new_node_callback = new_node_callback
        self.script_receiver = self.ScriptReceiver(job_manager)
        self.self_address = self.__get_local_ip_address()
        self.address_map = {}
        self.on_receive_finished_task_information_callback = on_receive_finished_task_information_callback
        self.finish = False

    def stop_server(self):
        self.server.close()
        self.handler.close()
        self.data_receive_selector.close()
        self.script_receiver.stop_receving()
        self.script_receiver.selector.close()
        print('server closed')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.close()
        self.handler.close()
        print('server closed')

    @staticmethod
    def __get_local_ip_address() -> str:
        ip_address = [l for l in (
            [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
                [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
                 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        print("local ip address is:" + ip_address)
        return ip_address

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
        self.handler.setblocking(False)
        self.data_receive_selector.register(self.handler, selectors.EVENT_READ, self.accept_information)
        while not self.finish:
            events = self.data_receive_selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
            # conn, addr = self.handler.accept()
            # with conn:
            #     address = addr[0]
            #     if address == self.self_address:
            #         continue
            #     data = conn.recv(1024)
            #     if not data:
            #         continue
            #     time_offset = (datetime.now() - self.time).microseconds
            #     split_data = data.decode().split(' ')
            #     available_slots = int(split_data[0])
            #     timestamp = str(split_data[1])
            #     address = addr[0]
            #     if timestamp != str(self.time.timestamp()):
            #         continue
            #     node_information = NodeInformation(address, available_slots, time_offset)
            #     print(node_information)
            #     self.new_node_callback(node_information)

    def accept_information(self, sock, mask):
        conn, addr = sock.accept()
        conn.setblocking(False)
        self.address_map[conn] = addr[0]
        self.data_receive_selector.register(conn, selectors.EVENT_READ, self.handle_information)

    def handle_information(self, conn, mask):
        try:
            addr = self.address_map[conn]
            if addr == self.self_address:
                return
            data = conn.recv(1024)
            if not data:
                return

            split_data = data.decode().split(' ')
            if split_data[0] == '1':
                self.__convert_broadcast_info(addr, split_data[1:])
            elif split_data[0] == '2':
                self.__convert_finished_information(split_data[1:])

        finally:
            conn.close()
            del self.address_map[conn]
            self.data_receive_selector.unregister(conn)

    def __convert_broadcast_info(self, addr: str, split_data: [str]):
        time_offset = (datetime.now() - self.time).microseconds
        available_slots = int(split_data[0])
        timestamp = str(split_data[1])
        if timestamp != str(self.time.timestamp()):
            return
        node_information = NodeInformation(addr, available_slots, time_offset)
        print(node_information)
        self.new_node_callback(node_information)

    def __convert_finished_information(self, split_data: [str]):
        print(split_data)
        task_id = split_data[0]
        finished_time = datetime.fromtimestamp(float(split_data[1]))
        self.on_receive_finished_task_information_callback(int(task_id), finished_time)

    class ScriptReceiver(Thread):
        def __init__(self, job_manager: JobManager):
            super().__init__()
            self.file_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.selector = selectors.DefaultSelector()
            self.connection_map = {}
            self.job_manager = job_manager
            self.file_receiver.bind(('0.0.0.0', script_file_recv_port))
            self.file_receiver.listen()
            self.file_receiver.setblocking(False)
            self.selector.register(self.file_receiver, selectors.EVENT_READ, self.accept)
            self.task_address_map = {}
            self.finish = False

        def stop_receving(self):
            self.file_receiver.close()

        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                self.file_receiver.close()
            except:
                print('close socket error')

        def accept(self, sock, mask):
            print('receive task offloading request')
            conn, addr = sock.accept()
            self.connection_map[conn] = addr
            conn.setblocking(False)
            self.selector.register(conn, selectors.EVENT_READ, self.read_script)

        def run(self) -> None:
            while not self.finish:
                events = self.selector.select()
                for key, mask in events:
                    # get the callback
                    callback = key.data
                    # calling callbak
                    callback(key.fileobj, mask)

        def get_original_address(self, task):
            return self.task_address_map[task]

        def del_task_recotd(self, task):
            del self.task_address_map[task]

        def read_script(self, conn, mask):
            addr = self.connection_map[conn]
            buffer_size = 2048
            file_name = 'script' + addr[0] + datetime.now().strftime('%Y_%m_%d%H_%M_%S') + '.py'
            print('receiving data...')
            try:
                task_id = int(str(conn.recv(5).decode()).strip())
                print("received task: " + str(task_id))
                with open(file_name, 'wb') as f:
                    data = conn.recv(1).decode()
                    while data == ' ':
                        data = conn.recv(1)
                    f.write(data.encode())
                    data = conn.recv(buffer_size)
                    while data:
                        f.write(data)
                        data = conn.recv(buffer_size)
                    conn.close()
                    del self.connection_map[conn]
                print('receive file over, start executing')
                task = ComputingTask(task_id, file_name, remote_task=True)
                self.task_address_map[task] = addr
                self.job_manager.add_task(task)
            except:
                print('receive error from' + addr[0])
            finally:
                self.selector.unregister(conn)


class NodeManger(Thread):
    def __init__(self, job_manager: JobManager, on_receive_finished_task_information_callback=None):
        super().__init__()
        self.client = ClientNode(job_manager)
        self.server = ServerNode(self.on_new_node_coming, job_manager, on_receive_finished_task_information_callback)
        self.job_manager = job_manager
        self.job_manager.remote_task_execution_finished_callback = self.__on_remote_task_execution_over
        self.nodes = {}
        self.best_nodes = []

    def stop_service(self):
        self.client.stop_service()
        self.server.stop_server()

    def run(self) -> None:
        self.server.start()
        self.client.start()

    def send_heart_beat(self):
        self.nodes = {}
        self.server.send_heart_beat()

    def send_task_to_best_node(self, task: ComputingTask, node: NodeInformation, error_callback=None):
        self.client.send_task(task, node, error_callback)

    def on_new_node_coming(self, node: NodeInformation):
        self.nodes[node.address] = node
        self.__refresh_best_nodes()

    def __refresh_best_nodes(self):
        def sort_node(node: NodeInformation, node2: NodeInformation) -> int:
            latency1 = node.latency
            latency2 = node2.latency
            available_slot1 = node.available_slots
            available_slot2 = node2.available_slots
            v1 = int(latency1 / available_slot1)
            v2 = int(latency2 / available_slot2)
            return v1 - v2

        self.best_nodes = sorted(self.nodes.values(), key=functools.cmp_to_key(sort_node), reverse=False)
        for n in self.best_nodes:
            print(n)

    def get_best_node(self, except_nodes=None) -> NodeInformation:
        if except_nodes is None:
            except_nodes = []
        for node in self.best_nodes:
            if node not in except_nodes and node.available_slots > 0:
                return node

    def __on_remote_task_execution_over(self, task: ComputingTask):
        print('remote task execution over')
        addr = self.server.script_receiver.get_original_address(task)
        self.client.send_task_execution_finish(task, addr[0])
        self.server.script_receiver.del_task_recotd(task)


if __name__ == '__main__':
    job_manager = JobManager()
    job_manager.start()
    node = NodeManger(job_manager)
    node.send_heart_beat()
    node.start()
    time.sleep(5)
