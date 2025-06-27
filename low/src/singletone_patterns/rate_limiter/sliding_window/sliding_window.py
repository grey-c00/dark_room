from collections import deque


class SlidingWindow:
    def __init__(self, window_max_size: int, window_time_interval_in_seconds: int):
        self.__window_max_size = window_max_size
        self.__window_time_interval_in_seconds = window_time_interval_in_seconds
        self.__dequeue = deque()

    def get_sliding_window_max_size(self) -> int:
        return self.__window_max_size

    def is_empty(self) -> bool:
        return len(self.__dequeue) == 0

    def get_no_requests_in_window(self) -> int:
        # TODO: consider clearing older requests
        return len(self.__dequeue)

    def is_full(self) -> bool:
        return self.get_sliding_window_max_size() == self.get_no_requests_in_window()

    def clear_older_requests(self, timestamp: float) -> None:
        while not self.is_empty() and self.__dequeue[0] <= timestamp:
            self.__dequeue.popleft()

    def get_window_time_interval_in_seconds(self) -> int:
        return self.__window_time_interval_in_seconds

    def add_request(self, request_timestamp: float) -> bool:
        if self.is_full():  # clearing out the older requests
            self.clear_older_requests(timestamp=request_timestamp-self.get_window_time_interval_in_seconds())

        if self.is_full():
            return False
        
        self.__dequeue.append(request_timestamp)
        print(f"added request in sliding window, size is updated to : {self.get_no_requests_in_window()}")
        return True
    
    def get_latest_request_timestamp(self) -> float:
        if self.is_empty():
            return -1
        
        return self.__dequeue[-1]
            
