import threading
from task_generator import TaskGenerator
from queue import Queue

class TaskHandler(threading.Thread):
    def __init__(self,max_tasks = 12, queue_empty_callback):
        self.tasks = Queue()
        self.callback = queue_empty_callback
        self.__max_tasks = max_tasks

    def run(self):
        while True:
            if len(self.tasks) == 0 and self.callback is not None:
                self.callback()
            new_task = self.tasks.get()
            new_task.run()
            new_task.join()
    
    def add_new_task(self,task:TaskGenerator):
        self.tasks.put(task)

    def get_queue_size(self)->int:
        return len(self.tasks)
    
    def is_full(self)->bool:
        return self.get_queue_size()>self.__max_tasks


if __name__ == '__main__':
    pass