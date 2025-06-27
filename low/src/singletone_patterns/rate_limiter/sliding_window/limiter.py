import time
import threading

from low.src.singletone_patterns.rate_limiter.sliding_window.sliding_window import SlidingWindow

class SlidingWindowRateLimiter:
    def __init__(self, window_max_size: int, window_time_interval_in_seconds: int):
        print("[SlidingWindowRateLimiter] Initializing")
        self.__window_max_size = window_max_size
        self.__window_time_interval_in_seconds = window_time_interval_in_seconds
        self.__in_memory_cache = {} # TODO: implement a smart and robut in-memory cache

        self.__stop_bg_tasks = False
        self._bg_tasks = threading.Thread(target=self.run_bg_tasks, daemon=True)
        self._bg_tasks.start()

    def get_window_time_interval_in_seconds(self) -> int:
        return self.__window_time_interval_in_seconds

    def is_request_id_present_in_cache(self, request_id: str) -> bool:
        return request_id in self.__in_memory_cache
    
    def get_new_sliding_window(self) -> SlidingWindow:
        return SlidingWindow(window_max_size=self.__window_max_size, window_time_interval_in_seconds=self.__window_time_interval_in_seconds)

    def register_request_in_cache_if_not_already_registered(self, request_id: str) -> bool:
        if self.is_request_id_present_in_cache(request_id=request_id):
            return True
        
        self.__in_memory_cache[request_id] = self.get_new_sliding_window()
        return True
    
    def update_in_memory_cache(self, request_id: str, request_timestamp: float) -> True:
        return self.__in_memory_cache[request_id].add_request(request_timestamp=request_timestamp)

    def is_request_allowed(self, request_id: str, request_timestamp: float) -> bool:
        self.register_request_in_cache_if_not_already_registered(request_id=request_id)
        req_allow_statue = self.update_in_memory_cache(request_id=request_id, request_timestamp=request_timestamp)
        if req_allow_statue:
            print(f"[SlidingWindowRateLimiter] Request {request_id} allowed")
        else:
            print(f"[SlidingWindowRateLimiter] Request {request_id} not allowed")
        return req_allow_statue
    
    def print_cache(self):
        print(f"[SlidingWindowRateLimiter] Printing cache, {len(self.__in_memory_cache)} request ids in cache")
        for request_id in self.__in_memory_cache:
            print(f"[SlidingWindowRateLimiter] Request {request_id} has {self.__in_memory_cache[request_id].get_no_requests_in_window()} requests")
    
    def clear_inactive_request_ids(self):
        print("[Bg_Task] Clearing inactive request ids")
        ids_in_cache = list(self.__in_memory_cache.keys())
        for request_id in ids_in_cache:
            self.__in_memory_cache[request_id].clear_older_requests(timestamp=time.time() - 2*self.get_window_time_interval_in_seconds())
            if self.__in_memory_cache[request_id].is_empty():
                del self.__in_memory_cache[request_id]

        self.print_cache()

        print("[Bg_Task] Cleared inactive request ids")

    def run_bg_tasks(self):
        while self.__stop_bg_tasks is False:
            time.sleep(4)
            self.clear_inactive_request_ids()

    def stop_bg_tasks(self):
        print("Stopping background tasks")
        self.__stop_bg_tasks = True
        self._bg_tasks.join()
        print("Background tasks stopped")

        