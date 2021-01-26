import threading
from task_generator import TaskGenerator
from queue import Queue

class TaskHandler(threading.Thread):
    def __init__(self,queue_empty_callback,max_tasks = 12):
        super().__init__()
        self.tasks = Queue()
        self.callback = queue_empty_callback
        self.__max_tasks = max_tasks

    def run(self):
        while True:
            if self.tasks.qsize() == 0 and self.callback is not None:
                self.callback()
            new_task = self.tasks.get()
            new_task.start()
            new_task.join()
    
    def add_new_task(self,task:TaskGenerator):
        self.tasks.put(task)

    def get_queue_size(self)->int:
        return self.tasks.qsize()
    
    def is_full(self)->bool:
        return self.get_queue_size()>self.__max_tasks


if __name__ == '__main__':
    pass