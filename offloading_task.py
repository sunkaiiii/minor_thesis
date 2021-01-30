import requests
import task_cacher
import sys
from task_cacher import CacheData

"""
offloading a file from the remote url
"""
def offloading_file(url):
    print("starting offloading url:"+url)
    r = requests.get(url,allow_redirects = True)
    id = task_cacher.create_id(url)
   
    data = CacheData(id,r.content)
    handler = task_cacher.CacheHandler()
     # the data will be saved in memory and might be saved in local storage
     # TODO persistance switch
    handler.cache_data(data,True)

def __send_data_back(data:CacheData):
    pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        offloading_file(sys.argv[1])
    else:
        offloading_file('https://photo-collection-monash.s3.amazonaws.com/00D35EC9-6845-48B0-B941-A83D85D74660.jpg')