from forward_table import ForwardTable
from uwb_handler import UWBHandler
from uwb_handler import UWBInformation
from sender_handler import SenderHandler
from task_handler import TaskHandler
from receiver_node import ReceiverTaskHandler
from task_generator import ComputingTask
from task_generator import TaskType
import task_generator
import threading
import asyncio
import time
from enum import Enum
class NodeType(Enum):
    Receiver = 1
    Sender = 2

class EdgeComputingNode(threading.Thread):
    def __init__(self):
        self.uwb_handler = UWBHandler()
        self.forward_table = ForwardTable()
        self.detect_node_thread = threading.Thread(target=self.detect_nodes)
        self.task_generator = task_generator.TaskGenerator(self.__handle_coming_task)
        self.task_handler = TaskHandler(self.__handle_queue_is_empty)
        self.node_type = NodeType.Receiver
        self.receiver = ReceiverTaskHandler()
        self.sender = SenderHandler()
        self.stop = False
    
    def run(self):
        self.detect_node_thread.run()
        self.task_generator.run()
        self.task_handler.run()
        self.__control_sender_and_receiver_service()

    
    def __control_sender_and_receiver_service(self):
        if self.node_type == NodeType.Receiver:
            self.receiver.start_service()
            self.uwb_handler.set_to_anchor_mode()
        elif self.node_type == NodeType.Sender:
            self.receiver.stop_service()
            self.uwb_handler.set_to_tag_mode()
            

    def __handle_coming_task(self,task:ComputingTask):
        if task.task_type == TaskType.LocalComputing or task.task_type == TaskType.LocalOffloading:
            self.task_handler.add_new_task(task)
        else:
            best_node = self.forward_table.get_the_best_node()
            if best_node is None:
                self.task_handler.add_new_task(task)
            else:
                self.sender.deliever_task(task,best_node)
        if self.task_handler.is_full() and self.node_type == NodeType.Receiver:
            self.node_type = NodeType.Sender
            self.__control_sender_and_receiver_service()

    def __handle_queue_is_empty(self):
        if self.node_type == NodeType.Sender:
            self.node_type = NodeType.Receiver
            self.__control_sender_and_receiver_service()


    def detect_nodes(self):
        while True:
            self.uwb_handler.detect_nodes(self.handle_uwb_information_callback)
            time.sleep(1)
        

    def handle_uwb_information_callback(self,uwb_list:[UWBInformation]):
        for node in uwb_list:
            print(node)
        self.forward_table.refresh_table(uwb_list)
        print(self.forward_table.best_device)


if __name__ == '__main__':
    # node = EdgeComputingNode()
    # node.detect_nodes()
    # import time
    # time.sleep(30)
    node = EdgeComputingNode()
    node.run()
    node.join()

