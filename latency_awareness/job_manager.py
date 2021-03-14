
import multiprocessing
from queue import Queue
from threading import Thread
class JobManager(Thread):
    def __init__(self):
        super().__init__()
        self.capacity = multiprocessing.cpu_count()*2
        self.task_queue = Queue(self.capacity)

    def available_slots(self)->int:
        return self.capacity - self.task_queue.qsize()

    def add_task(self,task:Thread):
        self.task_queue.put(task)

    def run(self):
        task = self.task_queue.get()
        task.start()
        task.join()