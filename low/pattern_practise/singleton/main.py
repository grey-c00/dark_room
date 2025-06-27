import threading
import time

from low.pattern_practise.singleton.singleton import Singleton

def get_singleton_object():
    for i in range(0,5):
        singleton_object = Singleton()
        res = singleton_object.get_singleton_object()
        print(f"[{threading.current_thread().name}] Object ID: {id(res)}")
        time.sleep(0.1)
    # Singleton.print_object_id(res)


def test_singleton_pattern():
    parallel_threads = 5
    threads = [threading.Thread(target=get_singleton_object, name=str(i)) for i in range(parallel_threads)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()



if __name__ == "__main__":
    test_singleton_pattern()