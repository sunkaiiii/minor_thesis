import requests
import task_cacher
from task_cacher import CacheData

def offloading_file(url):
    r = requests.get(url,allow_redirects = True)
    id = task_cacher.create_id(url)
    data = CacheData(id,r.content)
    handler = task_cacher.CacheHandler()
    handler.cache_data(data,True)


if __name__ == '__main__':
    offloading_file('https://photo-collection-monash.s3.amazonaws.com/00D35EC9-6845-48B0-B941-A83D85D74660.jpg')