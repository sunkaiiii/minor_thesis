from enum import Enum
from threading import Thread
import random
import time
from numpy import random
from datetime import datetime, timedelta


class ComputingTask:
    """
    The computing task contains an executable scirpt.
    """

    def __init__(self, id, script_name, deadline=None, except_nodes_id=[], remote_task=False, result_file_name=None):
        super().__init__()
        self.id = id
        self.script_name = script_name
        self.deadline = deadline
        self.except_nodes_id = except_nodes_id
        self.generated_time = datetime.now()
        self.is_multi_delievering = False
        self.force_local_handling = False
        self.remote_task = remote_task
        self.result_file_name = result_file_name

    def is_run_in_hurry(self) -> bool:
        if self.deadline is None:
            return False
        return (self.deadline - datetime.now()).seconds < 10


class TaskGenerator(Thread):
    """
    Randomly generate a task with a specific type.
    The types of a task will be four types
    """

    def __init__(self, callback, task_size=1200):
        super().__init__()
        self.callback = callback
        self.task_id = 0
        self.generate_over = False
        self.task_size = task_size
        self.deadline = random.poisson(lam=10, size=self.task_size)
        self.delay = random.poisson(lam=100, size=self.task_size)

    def run(self):
        while self.task_id < self.task_size:
            t = self.generate_task(self.task_id)
            self.task_id += 1
            self.callback(t)
            # time.sleep(random.randint(1,10))

            # the interval for generating a task may vary depending on different testing method.
            time.sleep(int(self.delay[self.task_id-1])/1000.0)
            # time.sleep(random.randint(1, 2) / 1000.0)
        self.generate_over = True

    def generate_task(self, id: int) -> ComputingTask:
        deadline = datetime.now() + timedelta(seconds=int(self.deadline[id]))
        seed = 0
        # t = ComputingTask(self.task_id, 'image_process_task.py', deadline=deadline)
        # if seed % 2 == 0:
        # t = ComputingTask(self.task_id, 'task.py', deadline=deadline)
        # else:
        t = ComputingTask(self.task_id, 'offloading_task.py', deadline=deadline, result_file_name='offloading_result.jpg')
        return t


if __name__ == '__main__':
    print(random.poisson(lam=1, size=1000))
    # task = ComputingTask(1)
    # task.start()
    # task.join()
