import multiprocessing as mp
import random
import time

NUM_WORKERS = 2
NUM_WRITERS = 10
TIMER = 3
MAXQSISE = 10
WRITE_INTERVAL = 0.2
WRITER_FUNC_VALUES = [0.05, 0.15]
WRITER_FUNC = random.uniform
LOG_ENABLED = False

def worker(name, q, done_q):
    """Queue processing unit.
    Will take task from queue and work on it.
    """
    while True:
        if not q.empty():
            task = q.get()
            if LOG_ENABLED:
                print(f"{name} get: {task}")
            time.sleep(task)
            done_q.put_nowait(task)
            q.task_done()


def write(name, q, den_q):
    """Process to write to a queue.
    Tweak it by changing parameters at the top of a program
    `WRITER_FUNC` - function to use to get time that
    worker processes will be "working" on a task

    `WRITE_INTERVAL` - determine how long process will "work" on a task
    `WRITER_FUNC_VALUES` - values to pass to a function,
    change them according to a function signature"""
    while True:
        task = WRITER_FUNC(*WRITER_FUNC_VALUES)
        time.sleep(WRITE_INTERVAL)
        if q.full():
            if LOG_ENABLED:
                print("Queue is full.")
            den_q.put_nowait(task)
        else:
            if LOG_ENABLED:
                print(f"{name} putting in queue.")
            q.put(task)


def count_q(name, q):
    """Process to count all items in queue
    just by getting item and increasing counter
    """
    count = 0
    while not q.empty():
        q.get()
        count += 1
        q.task_done()   
    print(f"In {name} queue where: {count}")

def get_task_count(queue, process):
    """Run special process to count items in queues
    I do need this because on MacOS method `qsize` is not implemented
    (
    """
    process.start()
    queue.join()
    process.terminate()


def starter(processes_list):
    """Start processes"""
    for processes in processes_list:
        for i in range(len(processes)):
            processes[i].start()

def terminator(processes_list):
    """Terminate processes"""
    for processes in processes_list:
        for i in range(len(processes)):
            processes[i].terminate()

def main():
    # Queue for requests
    # Main queue for tasks
    q = mp.JoinableQueue(maxsize=MAXQSISE)
    # Queue for done tasks
    done_q = mp.JoinableQueue()
    # Queue for denied tasks 
    # task is denied if main queue is full
    den_q = mp.JoinableQueue()

    # Little hack to count denied tasks queue
    # for some reasons on MacOS it wont let it count itself
    # if queue is empty
    den_q.put(1)

    # Dict to store workers objects
    workers = {}

    # Dict to store writers objects
    writers = {}

    # Create writer processes
    for i in range(NUM_WRITERS):
        writers[i] = mp.Process(target=write, args=(f"writer_{i}", q, den_q, ))

    # Create worker processes
    for i in range(NUM_WORKERS):
        workers[i] = mp.Process(target=worker, args=(f"worker_{i}", q, done_q, ))

    # Queues for succsess and unseccsessful tasks
    count_suc = mp.Process(target=count_q, args=("Succsess", done_q, ))
    count_den = mp.Process(target=count_q, args=("Denied", den_q, ))


    # start processes
    starter([writers, workers])

    # Terminate tasks at the end of timer
    # monotonic timer count time from begining of a program
    # in sec
    while True:
        if time.monotonic() > TIMER:
            terminator([writers, workers])
            if LOG_ENABLED:
                print("BREAKING")
            break
    

    # print succsefully processed and denied tasks
    print("------------------------")
    get_task_count(done_q, count_suc)
    get_task_count(den_q, count_den)


if __name__ == "__main__":
    start = time.time()
    main()
    print("Total work time: ", time.time() - start)
    