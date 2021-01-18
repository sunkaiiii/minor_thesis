import os
import random
import hashlib

class CacheData:
    def __init__(self,id:str,data:bytes):
        self.id = id
        self.data = data
def create_id(name:str)->str:
    return hashlib.sha1(name.encode()).hexdigest()

class CacheHandler:
    def __init__(self):
        self.cache_size = 200 # static allocation
        self.cache_dic = {}
    
    def cache_data(self,cache_data, persistance = False):
        self.cache_dic[cache_data.id] = cache_data
        if persistance:
            if not os.path.isdir('cache'):
                os.mkdir('cache')
            f = open(os.path.join("cache",cache_data.id),'wb')
            f.write(cache_data.data)
            f.close()
        if len(self.cache_dic) > self.cache_size:
            id = list(self.cache_dic.keys())[random.randint(0,self.cache_size-1)]
            del self.cache_dic[id]

    def get_cache_data(self,id) -> CacheData:
        if self.cache_dic.get(id) is not None:
            return self.cache_dic[id]
        file_path = os.path.join("cache",str(id))
        if os.path.exists(file_path):
            data = open(file_path,'rb').read()
            return CacheData(id,data)
        return None



if __name__ == '__main__':
    i = 0
    helper = CacheHandler()
    while i<300:
        data = CacheData(create_id(i),b"sadfasdasd")
        helper.cache_data(data,True)
        i+=1
