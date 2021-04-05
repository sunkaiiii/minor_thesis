import time
from node_manager import *
from task_generator import TaskGenerator
from task_generator import ComputingTask


class EdgeNode(Thread):
    def __init__(self):
        super(EdgeNode, self).__init__()
        self.job_manager = JobManager()
        self.node_manager = NodeManger(self.job_manager)
        self.task_generator = TaskGenerator(self.__handle_coming_task)

    def run(self) -> None:
        self.job_manager.start()
        self.task_generator.start()
        while True:
            print('send heart beat')
            self.node_manager.send_heart_beat()
            time.sleep(1)

    def __handle_coming_task(self, task: ComputingTask):
        print("task comes")
        if self.job_manager.available_slots() > 0:
            self.job_manager.add_task(task)
            return
        best_node = self.node_manager.get_best_node()
        print('try to send to best node')
        print(best_node)
        if best_node is None:
            print('No best node found')
            self.job_manager.add_task(task)
            return
        # Send node to the best node
        self.node_manager.send_task_to_best_node(task,best_node)

if __name__ == '__main__':
    node = EdgeNode()
    node.start()


