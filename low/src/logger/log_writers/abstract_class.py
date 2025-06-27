from abc import ABC, abstractmethod


class LogWriter(ABC):
    @abstractmethod
    def write_log(self, log: str) -> bool:
        pass
