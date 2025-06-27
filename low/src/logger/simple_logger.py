from enum import Enum

from low.src.logger.log_writers.abstract_class import LogWriter


class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    # WARNING = 3
    # ERROR = 4
    # CRITICAL = 5

class Logger:
    def __init__(self, log_level: LogLevel, log_writer: LogWriter):
        self.log_level = log_level
        self.log_writer = log_writer

    def log(self, message: str, log_level: LogLevel) -> bool:
        print(f"msg: {message}, log val: {log_level.value}, check is on: {self.log_level.value}")
        if log_level.value >= self.log_level.value:
            print("Successfully written")
            self.log_writer.write_log(message)
        return True

    def debug(self, message: str) -> bool:
        message = f"[DEBUG] {message}"
        self.log(message, LogLevel.DEBUG)
        return True

    def info(self, message: str) -> bool:
        message = f"[INFO] {message}"
        self.log(message, LogLevel.INFO)
        return True


# It is perfectly working code that will work