import multiprocessing as mp
import random

NUM_WORKERS = 2
RPS = 200
TIMER = 3
MAX_WORK_TIME = 3.0
WRITER_FUNC_VALUES = [0.1, 5.0]
WRITER_FUNC = random.uniform
LOG_ENABLED = False

def worker(name, q, done_q, den_q, connector):
    """Queue processing unit.
    Will take task from queue and work on it.
    """
    while True:
        if not q.empty():
            task = q.get()
            if LOG_ENABLED:
                print(f"{name} get: {task}")
            connector.send(task)
            if task >= float(MAX_WORK_TIME):
                den_q.put(task)
            else:
                done_q.put(task)
            q.task_done()

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
    q = mp.JoinableQueue()
    # Queue for done tasks
    done_q = mp.JoinableQueue()
    # Queue for denied tasks 
    # task is denied if main queue is full
    den_q = mp.JoinableQueue()

    # Little hack to count denied tasks queue
    # for some reasons on MacOS it wont let it count itself
    # if queue is empty
    den_q.put(1)


    # Pipe to communicate with worker processes
    parent, child = mp.Pipe()
    curent_time = 0

    # Dict to store workers objects
    workers = {}

    for _ in range(RPS * TIMER):
        task = WRITER_FUNC(*WRITER_FUNC_VALUES)
        q.put(task)
        if LOG_ENABLED:
            print("Putting: ", task)

    # Create worker processes
    for i in range(NUM_WORKERS):
        workers[i] = mp.Process(target=worker, args=(f"worker_{i}", q, done_q, den_q, child, ))

    # start processes
    starter([workers])

    while not q.empty():
        curent_time += parent.recv()
 
    terminator([workers])

    # print succsefully processed and denied tasks
    print("------------------------")
    print("Done task count:", done_q.qsize())
    print("Denied task count:",den_q.qsize())
    print("Work time: {:.2f}".format(curent_time))


if __name__ == "__main__":
    main()
    