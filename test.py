from queue import Queue
from cachetools import FIFOCache
from datetime import datetime

print(str(datetime.timestamp(datetime.now())))
cc = FIFOCache(maxsize=10000)
cc['item'] = [{'title' : 'sdfsf'}]
print(cc)

"""def update(queue):
    q = queue
    for i in range(10):
        q.put(i)


def remove(queue):
    q = queue
    while not q.empty():
        print(q.get())

q = Queue()

print(q.qsize())
update(q)
print(q.qsize())
print(list(q))"""
