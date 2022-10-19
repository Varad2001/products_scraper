import multiprocessing
import time
from multiprocessing import Pool


def hello():
    print("IN the hello function..")
    time.sleep(2)
    print("hello")


def main_func():
    print("In the main function...")
    time.sleep(2)
    print("Main function over..")



if __name__ == '__main__':
    print("IN the main module..")
    pool = Pool()
    pool.apply_async(hello).get()
    pool.apply_async(hello).get()
    print("Main module complete.")


