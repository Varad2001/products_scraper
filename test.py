import time
from multiprocessing import Queue, Process, Pool

def hello(i):
    print(f"Waiting for process : {i}")
    #time.sleep(2)
    print(f"hello : {i}")


if __name__ == "__main__":
    print("start")

    pool = Pool()
    i  = [i for i in range(1000)]

    for j in i:
        hello(j)

    a= pool.map_async(hello, i)
    print(a.get())


