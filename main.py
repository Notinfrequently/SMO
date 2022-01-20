import multiprocessing as mp
import random
import time

NUM_WORKERS = 100

def worker(name, q, done_q):
    while True:
        if not q.empty():
            task = q.get()
            print(f"{name} get: {task}")
            time.sleep(task)
            done_q.put_nowait(task)
            q.task_done()
            print("Done")


def count_q(q):
    count = 0
    while not q.empty():
        q.get()
        count += 1
        q.task_done()
    print("In queue where: ", count)


def main():
    # Queue for requests
    q = mp.JoinableQueue()
    done_q = mp.JoinableQueue()

    # Dict to store workers objects
    workers = {}

    # Populate task queue
    for _ in range(50):
        task = random.uniform(0.05, 0.15)
        print("Putting: ", task)
        q.put(task)

    for i in range(NUM_WORKERS):
        global worker
        workers[i] = mp.Process(target=worker, args=(f"worker_{i}", q, done_q, ))

    count = mp.Process(target=count_q, args=(done_q, ))

    # Worker process
    for i in range(NUM_WORKERS):
        workers[i].start()

    q.join()

    for i in range(NUM_WORKERS):
        workers[i].terminate()
    
    # Count queue with done tasks
    count.start()
    done_q.join()
    count.terminate()

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time() - start
    print(end)