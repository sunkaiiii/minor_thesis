from enum import Enum
from threading import Thread
import random
import time
import subprocess
import requests
from datetime import datetime, timedelta
import uuid


class TaskType(Enum):
    LocalComputing = 1
    LocalOffloading = 2
    EdgeComputing = 3
    EdgeOffloading = 4


class ComputingTask(Thread):
    """
    The computing task contains an executable scirpt.
    """

    def __init__(self, id, task_type: TaskType, deadline=None, except_nodes_id=[]):
        super().__init__()
        self.id = id
        self.deadline = deadline
        self.except_nodes_id = except_nodes_id
        self.is_multi_delievering = False
        self.task_type = task_type
        self.offloading_size = random.randint(100, 2000)

    def run(self):
        progress = 0
        while (progress < self.offloading_size):
            if progress > 0:
                time.sleep(1)
            progress += random.randint(100, 3000)

    def convert_edge_offloading_to_local_offloading(self):
        if self.task_type != TaskType.EdgeOffloading:
            raise Exception("The task type is not Edge Offloading")
        return ComputingTask(2, self.deadline, self.except_nodes_id)

    def convert_edge_computing_to_local_computing(self):
        if self.task_type != TaskType.EdgeComputing:
            raise Exception("The task type if not Edge Computing")
        return ComputingTask(self.id, 1)

    def is_run_in_hurry(self) -> bool:
        if self.deadline is None:
            return False
        return (self.deadline - datetime.now()).seconds < 15


def create_local_task(action):
    return ComputingTask(2, action)


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
            task = self.generate_task()
            self.task_id += 1
            self.callback(task)
            # time.sleep(random.randint(1,10))

            # the interval for generating a task may vary depending on different testing method.
            time.sleep(random.randint(1, 400) / 1000.0)
            if self.task_id == 2000:
                break

    def generate_task(self) -> ComputingTask:
        r = random.randint(1, 4)
        deadline = datetime.now() + timedelta(seconds=random.randint(5, 30))
        task = ComputingTask(self.task_id, r, deadline)
        return task


if __name__ == '__main__':
    task = ComputingTask(1)
    task.start()
    task.join()
