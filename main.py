from csv import writer
import multiprocessing as mp
import random
import time

NUM_WORKERS = 1
NUM_WRITERS = 1
TIMER = 5

def worker(name, q, done_q):
    while True:
        if not q.empty():
            task = q.get()
            print(f"{name} get: {task}")
            time.sleep(task)
            done_q.put_nowait(task)
            q.task_done()
            print("Done")


def write(name, q, den_q):
    while True:
        task = random.uniform(0.05, 0.15)
        time.sleep(0.2)
        if q.full():
            print("Queue is full.")
            den_q.put_nowait(task)
        else:
            print(f"{name} putting in queue.")
            q.put(task)


def count_q(name, q):
    count = 0
    while not q.empty():
        q.get()
        count += 1
        q.task_done()
    print(f"In {name} queue where: {count}")


def starter(processes_list):
    for processes in processes_list:
        for i in range(len(processes)):
            processes[i].start()

def terminator(processes_list):
    for processes in processes_list:
        for i in range(len(processes)):
            processes[i].terminate()

def main():
    # Queue for requests
    q = mp.JoinableQueue()
    done_q = mp.JoinableQueue()
    den_q = mp.JoinableQueue()
    den_q.put(1)

    # Dict to store workers objects
    workers = {}

    # Dict to store eriters objects
    writers = {}

    # Populate task queue
    for _ in range(10):
        task = random.uniform(0.05, 0.15)
        print("Putting: ", task)
        q.put(task)

    for i in range(NUM_WRITERS):
        writers[i] = mp.Process(target=write, args=(f"writer_{i}", q, done_q, ))

    for i in range(NUM_WORKERS):
        global worker
        workers[i] = mp.Process(target=worker, args=(f"worker_{i}", q, done_q, ))

    count_suc = mp.Process(target=count_q, args=("Succsess", done_q, ))
    count_den = mp.Process(target=count_q, args=("Denied", den_q, ))


    starter([writers, workers])

    """
    for i in range(NUM_WRITERS):
        writers[i].start()

    for i in range(NUM_WORKERS):
        workers[i].start()
    """
    q.join()

    terminator([writers, workers])
    """
    for i in range(NUM_WORKERS):
        workers[i].terminate()
    
    for i in range(NUM_WRITERS):
        writers[i].terminate()
    
    if time.monotonic > TIMER:
    """

    count_den.start()
    den_q.join()
    count_den.terminate()

    # Count queue with done tasks
    count_suc.start()
    done_q.join()
    count_suc.terminate()






if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time() - start
    print(end)