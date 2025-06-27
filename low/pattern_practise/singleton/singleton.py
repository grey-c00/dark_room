import threading


class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("[ThreadSafe] allocating memory for the object")
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def print_object_id(obj):
        if obj is None:
            print("No object is received, skipping id")
            return
        print(f"Object id is: {id(obj)}")

    @classmethod
    def get_singleton_object(cls):
        return cls._instance