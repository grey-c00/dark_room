from enum import Enum
import time
from typing import Optional

class ProcessState(Enum):
    RUNNING = 1
    KILLED = 2

    def __str__(self):
        return super().__str__()

class Process:
    def __init__(self, pid: int):
        self.pid = int(pid)
        self.start_time = None
        self.end_time = None
        self.state = None

    def __str__(self):
        return f"pid: {self.pid}, state: {print(self.state)}, start_time: {self.get_start_time()}, end_time: {self.get_end_time()}"
    
    def get_pid(self) -> int:
        return self.pid
    
    def start(self) -> int:
        self.start_time = time.time()
        self.state = ProcessState.RUNNING
        return 0

    def end(self) -> int:
        self.end_time = time.time()
        self.state = ProcessState.KILLED
        return 0
    
    def is_running(self) -> int:
        return self.state == ProcessState.RUNNING
    
    def is_killed(self) -> int:
        return self.state == ProcessState.KILLED
    
    def get_end_time(self) -> Optional[float]:
        return self.end_time
    
    def get_start_time(self) -> float:
        return self.start_time



class ProcessManager:
    def __init__(self):
        """
        TODO: Write a logic to generate a unique PID whenever a process requests ID
        """
        self.process_map = dict()
        self.all_processes = list()
        self._cursor = 0 # can be manged via a special class

    def _get_process_count(self) -> int:
        return len(self.all_processes)
    
    def _add_process_to_pool(self, process: Process) -> None:
        self.all_processes.append(process)

    def _is_running(self, pid: int) -> bool:...

    def _get_process_index(self, pid: int) -> Optional[int]:
        return self.process_map.get(pid)
    
    def _end(self, idx: int) -> None:
        process = self._get_process_from_idx(idx=idx)
        process.end()
        self._update_process_at_idx(idx=idx, process=process)

    def _is_empty(self) -> bool: ...

    def _get_cursor_idx(self) -> int:
        return self._cursor
    
    def _move_cursor_to_next(self):
        self._cursor += 1

    def _cursor_at_end(self) -> bool:
        return self._get_cursor_idx() == len(self.all_processes)
    
    def _update_process_at_idx(self, idx: int, process: Process):
        self.all_processes[idx] = process

    def _get_process_from_idx(self, idx: int) -> Process:
        return self.all_processes[idx]

    def start(self, pid: int) -> None:
        """
        TODO: validations such as
            1. if already running -> can be ignored or raised error
            2. if killed -> flow can be discussed and decided
        """
        _process = Process(pid=pid)
        _process.start()
        self.process_map[pid] = self._get_process_count()
        self._add_process_to_pool(_process)
    
    def end(self, pid: int) -> None:
        """
        TODO:
            1. cleanup logic from list and map -> probably bucketing is one of the efficient way
        """
        idx = self._get_process_index(pid)
        self._end(idx=idx)

    def poll(self, poll_time: int = None) -> Optional[Process]:
        if poll_time is None:
            poll_time = time.time()
        if self._cursor_at_end():
            return None
        
        idx = self._get_cursor_idx()

        process = self._get_process_from_idx(idx=idx)

        if process.is_killed():
            self._move_cursor_to_next()
            # TODO: check this race condition in multi threaded environment
            # if process.get_end_time() <= poll_time: 
            #     return self.poll(poll_time=poll_time)
        return process
        
        




