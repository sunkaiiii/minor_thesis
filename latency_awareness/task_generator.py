from enum import Enum
from threading import Thread
import random
import time
from datetime import datetime, timedelta


class ComputingTask(Thread):
    """
    The computing task contains an executable scirpt.
    """

    def __init__(self, id, deadline=None, except_nodes_id=[]):
        super().__init__()
        self.id = id
        self.deadline = deadline
        self.except_nodes_id = except_nodes_id
        self.is_multi_delievering = False
        self.offloading_size = random.randint(100, 2000)

    def run(self):
        progress = 0
        while progress < self.offloading_size:
            if progress > 0:
                time.sleep(1)
            progress += random.randint(100, 3000)

    def is_run_in_hurry(self) -> bool:
        if self.deadline is None:
            return False
        return (self.deadline - datetime.now()).seconds < 15


class TaskGenerator(Thread):
    """
    Randomly generate a task with a specific type.
    The types of a task will be four types
    """

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.task_id = 0

    def run(self):
        while True:
            t = self.generate_task()
            self.task_id += 1
            self.callback(t)
            # time.sleep(random.randint(1,10))

            # the interval for generating a task may vary depending on different testing method.
            time.sleep(random.randint(1, 400) / 1000.0)
            if self.task_id == 2000:
                break

    def generate_task(self) -> ComputingTask:
        deadline = datetime.now() + timedelta(seconds=random.randint(5, 30))
        t = ComputingTask(self.task_id, deadline)
        return t


if __name__ == '__main__':
    task = ComputingTask(1)
    task.start()
    task.join()
