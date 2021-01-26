from enum import Enum
from threading import Thread
import random
import time

class TaskType(Enum):
    LocalComputing = 1
    LocalOffloading = 2
    EdgeComputing = 3
    EdgeOffloading = 4

class ComputingTask(Thread):
    """
    The computing task contains an executable scirpt.
    """
    def __init__(self, task_type,action):
        super().__init__()
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
        # print(str(self.task_type))
        # TODO sending the script file
        self.action()


class TaskGenerator(Thread):
    """
    Randomly generate a task with a specific type.
    The types of a task will be four types
    """
    def __init__(self,callback):
        super().__init__()
        self.callback = callback
    
    def run(self):
        while True:
            task = self.generate_task()
            self.callback(task)
            # time.sleep(random.randint(1,10))

            # the interval for generating a task may vary depending on different testing method.
            time.sleep(0.2)


    def generate_task(self)->ComputingTask:
        r = random.randint(1,4)

        #TODO the action would be vary depending on the type of the task
        task = ComputingTask(r,self.default_action)
        return task
    
    def default_action(self):
        time.sleep(random.randint(1,10))
        pass
