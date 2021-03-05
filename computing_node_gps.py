from gps_forward_table import GPSForwardTable
from gps_sender_recorder import GPSSenderRecorder
from data_reader import CarDrivingData
from data_reader import read_filterd_selected_data
from task_handler import TaskHandler
from task_generator_gps import ComputingTask
from gps_info_handler import GPSInformationHandler
from datetime import datetime
import task_generator_gps
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
        all_filted_data = read_filterd_selected_data()
        self.gps_handler = GPSInformationHandler(all_filted_data[2])
        self.other_gps_nodes = []
        all_filted_data = all_filted_data[3:]
        self.other_gps_nodes = [GPSInformationHandler(d) for d in all_filted_data]
        self.forward_table = GPSForwardTable()
        self.task_generator = task_generator_gps.TaskGenerator(
            self.__handle_coming_task)
        self.task_handler = TaskHandler(
            queue_empty_callback=self.__handle_queue_is_empty)
        self.node_type = NodeType.Receiver
        self.sender = GPSSenderRecorder()
        self.maximum_multi_deliever_number = 4

    def run(self):
        print("start edge computing services")
        self.task_generator.start()
        self.task_handler.start()
        self.detect_nodes()
        # self.__control_sender_and_receiver_service()
        self.task_generator.join()

    def __handle_coming_task(self, task: ComputingTask):
        print("task is generated")
        if self.task_handler.is_full():
            best_node = self.forward_table.get_the_best_node()
            if best_node is None or best_node.distance > 700:
                self.task_handler.add_new_task(task)
            else:
                print('deleiver task: '+str(task.id)+' to ' + str(best_node.data.id))
                self.sender.deliever_task(task,self.gps_handler.current_gps_data,best_node.data)
        else:
            self.task_handler.add_new_task(task)


    def __handle_queue_is_empty(self):
        print("queue is empty")



    def detect_nodes(self):
        while self.task_generator.is_alive():
            current_data = map(lambda x:x.current_gps_data,self.other_gps_nodes)
            self.forward_table.refresh_table(self.gps_handler.current_gps_data,list(current_data))
            time.sleep(1)
        # self.uwb_handler.detect_nodes(self.handle_uwb_information_callback)
        # while not self.stop:
        #     time.sleep(1)
        # self.uwb_handler.stop_detect_nodes()



if __name__ == '__main__':
    # node = EdgeComputingNode()
    # node.detect_nodes()
    # import time
    # time.sleep(30)
    node = EdgeComputingNode()
    # node.detect_nodes()
    node.start()
    node.join()
