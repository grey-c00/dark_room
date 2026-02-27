import time
import threading
import requests

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        print(f"time taken by func: {func.__name__} is: {end_time-start_time}")
        return res
    

    return wrapper

class GIL:
    def __init__(self):
        pass


    @staticmethod
    def run_loop(i=2):
        for i in range(10**i):
            res = requests.get("https://www.google.com/")

    @staticmethod
    @timeit
    def run_single_fun():
        GIL.run_loop()

    @staticmethod
    @timeit
    def run_parallel_loops():
        thread_one = threading.Thread(target=GIL.run_loop)
        thread_two = threading.Thread(target=GIL.run_loop)

        thread_one.start()
        thread_two.start()

        thread_one.join()
        thread_two.join()




    
gil_obj = GIL()

gil_obj.run_single_fun()

gil_obj.run_parallel_loops()

# gil_obj.run_loop(1)