from enum import Enum
from threading import Thread
import random
import time
from datetime import datetime, timedelta


class ComputingTask:
    """
    The computing task contains an executable scirpt.
    """

    def __init__(self, id, script_name, deadline=None, except_nodes_id=[],remote_task=False):
        super().__init__()
        self.id = id
        self.script_name = script_name
        self.deadline = deadline
        self.except_nodes_id = except_nodes_id
        self.generated_time = datetime.now()
        self.is_multi_delievering = False
        self.force_local_handling = False
        self.remote_task = remote_task

    def is_run_in_hurry(self) -> bool:
        if self.deadline is None:
            return False
        return (self.deadline - datetime.now()).seconds < 10


class TaskGenerator(Thread):
    """
    Randomly generate a task with a specific type.
    The types of a task will be four types
    """

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.task_id = 0
        self.generate_over = False

    def run(self):
        while self.task_id < 2000:
            t = self.generate_task()
            self.task_id += 1
            self.callback(t)
            # time.sleep(random.randint(1,10))

            # the interval for generating a task may vary depending on different testing method.
            time.sleep(random.randint(1, 400) / 1000.0)
            # time.sleep(random.randint(1, 2) / 1000.0)
        self.generate_over = True

    def generate_task(self) -> ComputingTask:
        deadline = datetime.now() + timedelta(seconds=random.randint(5, 30))
        t = ComputingTask(self.task_id, 'task.py', deadline=deadline)
        return t


if __name__ == '__main__':
    task = ComputingTask(1)
    task.start()
    task.join()
