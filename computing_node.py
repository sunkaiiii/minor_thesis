from forward_table import ForwardTable
from uwb_handler import UWBHandler
from uwb_handler import UWBInformation
import task_generator
import threading
import asyncio
import time
edge_task_quee = []
class EdgeComputingNode(threading.Thread):
    def __init__(self):
        self.uwb_handler = UWBHandler()
        self.forward_table = ForwardTable()
        self.detect_node_thread = threading.Thread(target=self.detect_nodes)
        self.task_generator = task_generator.TaskGenerator(self.__handle_coming_task)
    
    def run(self):
        self.detect_node_thread.run()
        self.task_generator.run()
        time.sleep(100)
        
    def __handle_coming_task(self,task):
        task.run()

    def detect_nodes(self):
        while True:
            self.uwb_handler.detect_nodes(self.handle_uwb_information_callback)
            time.sleep(1)
        

    def handle_uwb_information_callback(self,uwb_list:[UWBInformation]):
        for node in uwb_list:
            print(node)
        self.forward_table.refresh_table(uwb_list)
        print(self.forward_table.best_id)


if __name__ == '__main__':
    # node = EdgeComputingNode()
    # node.detect_nodes()
    # import time
    # time.sleep(30)
    node = EdgeComputingNode()
    node.run()
    node.join()

