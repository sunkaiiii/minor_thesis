from forward_table import ForwardTable
from forward_table import DistanceRecord
from uwb_handler import UWBHandler
from sender_handler import SenderHandler
from task_handler import TaskHandler
from receiver_node import ReceiverTaskHandler
from receiver_node import multi_delievering_record
from task_generator import ComputingTask
from task_generator import TaskType
from receiver_node import MultiTaskDelieveringRecord
from datetime import datetime
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
        super().__init__()
        self.uwb_handler = UWBHandler()
        self.forward_table = ForwardTable()
        self.detect_node_thread = threading.Thread(target=self.detect_nodes)
        self.task_generator = task_generator.TaskGenerator(
            self.__handle_coming_task)
        self.task_handler = TaskHandler(
            queue_empty_callback=self.__handle_queue_is_empty)
        self.node_type = NodeType.Receiver
        self.receiver = ReceiverTaskHandler(self.task_handler)
        self.receiver.setDaemon(True)
        self.sender = SenderHandler(self.__handle_offloading_error)
        self.stop = False
        self.maximum_multi_deliever_number = 4

    def run(self):
        print("start edge computing services")
        self.receiver.start()
        self.task_generator.start()
        self.task_handler.start()
        # self.__control_sender_and_receiver_service()
        self.task_generator.join()

    def __control_sender_and_receiver_service(self):
        if self.node_type == NodeType.Receiver:
            print("start to change the node to Receiver")
            self.receiver.start_service()
            self.uwb_handler.set_to_anchor_mode()
            self.stop = True
        elif self.node_type == NodeType.Sender:
            self.receiver.stop_service()
            self.uwb_handler.set_to_tag_mode()
            self.stop = False
            self.detect_node_thread.start()
            print("start to change the node to Sender")

    def __handle_coming_task(self, task: ComputingTask, previous_information: DistanceRecord = None):
        print("task is generated")
        if task.task_type == TaskType.LocalComputing or task.task_type == TaskType.LocalOffloading:
            self.task_handler.add_new_task(task)
        else:
            best_node = self.forward_table.get_the_best_node(
                task.except_nodes_id)
            if best_node is None:
                print("No best node is found, convert to local task")
                if task.task_type == TaskType.EdgeOffloading:
                    task = task.convert_edge_offloading_to_local_offloading()
                elif task.task_type == TaskType.EdgeComputing:
                    task = task.convert_edge_computing_to_local_computing()
                self.task_handler.add_new_task(task)
            else:
                if task.is_run_in_hurry():
                    best_node_ids = [best_node.id]
                    best_nodes = [best_node]
                    i = 1
                    while i < self.maximum_multi_deliever_number:
                        other_best_nodes = self.forward_table.get_the_best_node(
                            best_node_ids)
                        if other_best_nodes is not None:
                            best_nodes.append(other_best_nodes)
                            best_node_ids.append(other_best_nodes.id)
                    self.__handle_with_multi_task_delievering(task, best_nodes)
                else:
                    self.sender.deliever_task(task, best_node)
        if self.task_handler.is_full() and self.node_type == NodeType.Receiver:
            self.node_type = NodeType.Sender
            self.__control_sender_and_receiver_service()

    def __handle_with_multi_task_delievering(self, task: ComputingTask, nodes: [DistanceRecord]):
        task.is_multi_delievering = True
        multi_delievering_record[task] = MultiTaskDelieveringRecord()
        for node in nodes:
            multi_delievering_record[task].delievering_count += 1
            self.sender.deliever_task(task, node)

    def __handle_queue_is_empty(self):
        print("queue is empty")
        if self.node_type == NodeType.Sender:
            self.node_type = NodeType.Receiver
            self.__control_sender_and_receiver_service()

    def __handle_offloading_error(self, task: ComputingTask, distance_record: DistanceRecord):
        if task.is_multi_delievering:
            task_record = multi_delievering_record.get(task)
            if task_record is None or task_record.is_returned:
                return
            task_record.delievering_count -= 1
            if task_record.delievering_count <= 0:
                local_task = self.__convert_task_to_local_task(task)
                self.__handle_coming_task(local_task, distance_record)

        else:
            print("One task is sending failure, the deadline sub with current time is" +
                  str((task.deadline-datetime.now()).seconds))
            task.except_nodes_id.append(distance_record.id)
            if (task.deadline - datetime.now()).seconds < 20:
                print("The failure task has been changed to local task")
                task = self.__convert_task_to_local_task(task)
            self.__handle_coming_task(task, distance_record)

    def __convert_task_to_local_task(self, task: ComputingTask) -> ComputingTask:
        if task.task_type == TaskType.EdgeComputing:
            return task.convert_edge_computing_to_local_computing()
        elif task.task_type == TaskType.EdgeOffloading:
            return task.convert_edge_offloading_to_local_offloading()

    def detect_nodes(self):
        self.uwb_handler.detect_nodes(self.handle_uwb_information_callback)
        while not self.stop:
            time.sleep(1)
        self.uwb_handler.stop_detect_nodes()

    def handle_uwb_information_callback(self, uwb_list: [DistanceRecord]):
        for node in uwb_list:
            print(node)
        self.forward_table.refresh_table(uwb_list)


if __name__ == '__main__':
    # node = EdgeComputingNode()
    # node.detect_nodes()
    # import time
    # time.sleep(30)
    node = EdgeComputingNode()
    node.start()
    node.join()
