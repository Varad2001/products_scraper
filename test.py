import multiprocessing
import threading
import time

import schedule

def say_hello():
    print("Hello, I am Varad.")

def dojob():
    i = 0
    schedule.clear('mytask')
    print("Previous jobs clear.")
    schedule.every(2).seconds.do(say_hello).tag("mytask")
    schedule.run_all()
    time.sleep(2)
    print("Created new job.")
    while True:
        print(i)
        if not schedule.get_jobs("mytask"):
            print("No task to run.")
            break
        schedule.run_pending()
        time.sleep(2)
        if i == 50:
            schedule.clear('mytask')
            print("Stopping background task and exiting...")
            break
        i += 1


def update_items(name):
    print("From proc : ", name)
    print("updating items")
    time.sleep(2)
    print("update complete.")


def begin_update_process(update_time):
    print("Update time:", update_time)
    # clear previous running jobs
    schedule.clear("update_process")

    # set the update time
    schedule.every(int(update_time)).seconds.do(update_items, name=update_time).tag("update_process")
    print("Created new job.")

    time.sleep(1)
    # run the update process once in the background
    new_thread = threading.Thread(target=update_items, args=(update_time,))
    new_thread.start()

    # sleep for update_time to ensure scheduler puts the process in pending jobs
    time.sleep(update_time)

    while True:
        if not schedule.get_jobs("update_process"):
            print(f"No job pedning. ")
            time.sleep(1)
            continue

        schedule.run_pending()
        time.sleep(update_time)

    print("Ending this update process.")

if __name__ == "__main__":
    print("In main function...")
    time.sleep(4)
    print("Killing prev proc...")
    procs = multiprocessing.active_children()
    for proc in procs:
        if proc.name == 'update_process':
            proc.kill()

    print("Starting other proc..")
    time.sleep(2)
    proc = multiprocessing.Process(target=begin_update_process, args=(8,), name="update_process")
    proc.start()