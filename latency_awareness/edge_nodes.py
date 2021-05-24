import time
import csv
from node_manager import *
from task_generator import TaskGenerator
from task_generator import ComputingTask


class EdgeNode(Thread):
    def __init__(self, log_file=None, sort_strategy = 2):
        super(EdgeNode, self).__init__()
        self.job_manager = JobManager(self.__task_done_locally)
        self.node_manager = NodeManger(self.job_manager,
                                       on_receive_finished_task_information_callback=self.__receive_task_finished_information,sort_strategy = sort_strategy)
        self.task_generator = TaskGenerator(self.__handle_coming_task)
        if log_file is not None:
            self.logger = csv.writer(log_file, delimiter=',', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
        self.remote_task_map = {}

    def run(self) -> None:
        self.node_manager.start()
        self.job_manager.start()
        self.task_generator.start()
        while not self.task_generator.generate_over:
            print('send heart beat')
            self.node_manager.send_heart_beat()
            time.sleep(1)
        print('stopping service')
        self.job_manager.finished = True
        print('wait for job manager')
        self.job_manager.join()
        retry = 0
        print('wait for remote execution')
        while retry < 10:
            if len(self.remote_task_map) == 0:
                break
            time.sleep(1)
            retry += 1
        print('execution finished')
        self.node_manager.stop_service()


    def run_as_receiver(self):
        self.node_manager.start()
        self.job_manager.start()

    def __handle_coming_task(self, task: ComputingTask):
        print("task comes: "+str(task.id))
        if self.job_manager.available_slots() > 0 or task.force_local_handling:
            self.job_manager.add_task(task)
            return
        best_node = self.node_manager.get_best_node(task.except_nodes_id)
        if best_node is None:
            print('No best node found')
            self.job_manager.add_task(task)
            return
        # Send node to the best node
        print('try to send '+ str(task.id) + ' to best node' + str(best_node))
        self.node_manager.send_task_to_best_node(task, best_node, self.__remote_execution_error)
        self.remote_task_map[task.id] = (task, best_node)

    def __task_done_locally(self, task: ComputingTask):
        if self.logger is None:
            return
        self.logger.writerow(
            ['task', str(task.id), str(task.generated_time), str(task.deadline), str(datetime.now()),
             str(datetime.now() < task.deadline),
             str(True), '', ''])

    def __remote_execution_error(self, task: ComputingTask, node: NodeInformation):
        print('task ' + str(task.id) + " remote executing error by " + str(node))
        del self.remote_task_map[task.id]
        if task.is_run_in_hurry():
            task.force_local_handling = True
        else:
            task.except_nodes_id.append(node.address)
        self.logger.writerow(
            ['task', str(task.id), str(task.generated_time), str(task.deadline), str(datetime.now()),
             str(datetime.now() < task.deadline),
             str(False), str(node.address), str(node.latency)])
        self.__handle_coming_task(task)

    def __receive_task_finished_information(self, task_id: int, finished_time: datetime):
        try:
            print('task ' + str(task_id) + ' remote execution finished')
            task = self.remote_task_map[task_id][0]
            node = self.remote_task_map[task_id][1]
            del self.remote_task_map[task_id]
            self.logger.writerow(['task', str(task.id), str(task.generated_time), str(task.deadline), str(datetime.now()),
                                  str(datetime.now() < task.deadline), str(True), str(node.address), str(node.latency)])
        except Exception as e:
            print(e)


if __name__ == '__main__':
    node = EdgeNode()
    node.run_as_receiver()
    print(node.job_manager.remote_task_execution_finished_callback)
