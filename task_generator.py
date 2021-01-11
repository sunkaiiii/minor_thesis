from enum import Enum
from threading import Thread
import random

class TaskType(Enum):
    LocalComputing = 1
    LocalOffloading = 2
    EdgeComputing = 3
    EdgeOffloading = 4

class ComputingTask(Thread):
    def __init__(self, task_type,action):
        self.action = action
        if task_type == 1:
            self.task_type = TaskType.LocalComputing
        elif task_type == 2:
            self.task_type = TaskType.LocalOffloading
        elif task_type == 3:
            self.task_type = TaskType.EdgeComputing
        elif task_type == 4:
            self.task_type = TaskType.EdgeOffloading
        else:
            raise TypeError
    def run(self):
        self.action()


class TaskGenerator:
    def generate_task(self):
        r = random.randint(TaskType.LocalComputing,TaskType.EdgeOffloading)
        return ComputingTask(r,self.default_action)
    
    def default_action(self):
        pass

