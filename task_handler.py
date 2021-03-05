import threading
from threading import Thread
from task_generator import ComputingTask
from task_generator import TaskGenerator
from queue import Queue

class TaskHandler(threading.Thread):        
    """
    The task handler has an execution queue, which will handle all the task execution.
    When the number of task over the limited number of tasks, the queue will block the addition.
    The local tasks and remote offloading tasks will share the capacity of the queue.
    The size of the queue will influence the reaction of the computing node.
    when the queue is empty, it will invoke the callback to indicate that the node is available to receive offloading tasks.
    """
    def __init__(self,queue_empty_callback,max_tasks = 12):
        super().__init__()
        self.tasks = Queue()
        self.callback = queue_empty_callback
        self.__max_tasks = max_tasks


    def run(self):
        """
        The thread will run forever until the program dead.
        the task running in this thread will execute sequentially.
        """
        while True:
            # When the queue is empty, invoke the call back to indicate the availability of the queue.
            if self.tasks.qsize() == 0 and self.callback is not None:
                self.callback()
            new_task = self.tasks.get()
            new_task.start()
            new_task.join()
    
    def add_new_task(self,task:ComputingTask):
        self.tasks.put(task)

    def get_queue_size(self)->int:
        return self.tasks.qsize()
    
    def is_full(self)->bool:
        return self.get_queue_size()>self.__max_tasks


if __name__ == '__main__':
    pass