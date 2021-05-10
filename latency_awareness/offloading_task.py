import requests
import task_cacher
import sys
from task_cacher import CacheData
import random


def generating_offloading_url() -> str:
    urls = ['https://photo-collection-monash.s3.amazonaws.com/20161128_032955000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161128_033042000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_004901000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_004921000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005003000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005023000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005057000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005118000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005128000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005132000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005154000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005204000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005211000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161205_005232000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010508000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010539000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010553000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010621000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010650000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010753000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010831000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010857000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010910000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_010932000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_011257000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_011310000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_011323000_iOS.jpg'
        , 'https://photo-collection-monash.s3.amazonaws.com/20161226_011329000_iOS.jpg']
    index = random.randint(0, len(urls) - 1)
    return urls[index]


handler = task_cacher.CacheHandler()
"""
offloading a file from the remote url
"""


def offloading_file(url):
    print("starting offloading url:" + url)
    id = task_cacher.create_id(url)
    data = handler.get_cache_data(id)
    if data is not None:
        f = open("offloading_result.jpg",'wb')
        f.write(data.data)
        f.close()
        return
    r = requests.get(url, allow_redirects=True)
    data = CacheData(id, r.content)
    # the data will be saved in memory and might be saved in local storage
    # TODO persistance switch
    handler.cache_data(data, True)
    with open("offloading_result.jpg",'wb') as f:
        f.write(data.data)


def __send_data_back(data: CacheData):
    pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        offloading_file(sys.argv[1])
    else:
        offloading_file(generating_offloading_url())
