from enum import Enum
from threading import Thread
import random
import computing_node
import time

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
        print(str(self.task_type))
        self.action()


class TaskGenerator(Thread):
    def __init__(self,callback):
        self.callback = callback
    
    def run(self):
        while True:
            task = self.generate_task()
            self.callback(task)
            time.sleep(random.randint(1,10))


    def generate_task(self)->ComputingTask:
        r = random.randint(1,4)
        task = ComputingTask(r,self.default_action)
        return task
    
    def default_action(self):
        pass
