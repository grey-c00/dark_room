from low.src.logger.log_writers.abstract_class import LogWriter


class LogWriterInFile(LogWriter):
    def __init__(self, file_path: str, buffer_threshold: int, log_line_separator: str = "\n"):
        # Assuming only one file will be there, instead we can create multiple files based on
        # - time stamp, read and retrival will be easy
        # - number of rows
        self.file_path = file_path
        self.buffer_threshold = buffer_threshold
        self.log_line_separator = log_line_separator
        self.buffer = []

    def persist_buffer_asynchronously(self) -> bool:
        with open(self.file_path, 'a') as file:
            for line in self.buffer:
                file.write(line)
                file.write(self.log_line_separator)
        return True

    def write_through_buffer(self, log: str) -> bool:
        self.buffer.append(log)
        if len(self.buffer) >= self.buffer_threshold:
            # TODO: make is async
            # TODO: make it thread safe
            self.persist_buffer_asynchronously()
            self.buffer = []
        return True


    def write_log(self, log) -> bool:
        # TODO: Handle error
        return self.write_through_buffer(log)

