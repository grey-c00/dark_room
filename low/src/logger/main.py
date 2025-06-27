import time
from low.src.logger.log_writers.file import LogWriterInFile
from low.src.logger.simple_logger import Logger, LogLevel


def test_file_logger():
    print("Testing file logger")
    log_file_path = "//low/src/logger/test_outputs/log_file.txt"
    buffer_threshold = 2
    log_writer = LogWriterInFile(file_path=log_file_path,
                                 buffer_threshold=buffer_threshold
                                 )
    logger =Logger(log_level=LogLevel.INFO,
                   log_writer=log_writer
                   )

    logger.debug("START")

    logger.debug(f"This is debug msg at time {time.time()}")
    logger.debug(f"This is debug msg at time {time.time()}")
    logger.info(f"This is info msg at time {time.time()}")
    logger.info(f"This is info msg at time {time.time()}")
    logger.debug("SUCCESS")


if __name__ == "__main__":
    print("Starting main")
    test_file_logger()