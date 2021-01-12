from queue import Queue
import os
class CacheHandler:
    def __init__(self):
        self.cache_size = 200 # static allocation
        self.cache_queue = Queue(self.cache_size)
    
    def cache_data(self,cache_data, persistance = False):
        self.cache_queue.put(cache_data)
        if persistance:
            if not os.path.isdir('cache'):
                os.mkdir('cache')
            f = open(os.path.join("cache",str(cache_data.id)),'w')
            f.write(cache_data.data)
            f.close()


class CacheData:
    def __init__(self,id,data):
        self.id = id
        self.data = data

if __name__ == '__main__':
    data = CacheData(123,"sadfasdasd")
    helper = CacheHandler()
    helper.cache_data(data,True)