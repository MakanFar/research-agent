import logging
import time
from pathlib import Path
from functools import wraps

class Logger:
    def __init__(self, name: str = "research-agent", log_file: str = "logs/app.log", level=logging.DEBUG):
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # capture everything in file
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.WARNING)  # only show warnings and errors to user
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger

    def log_execution_time(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.time()
            self.logger.debug(f"Started `{fn.__name__}`")
            result = fn(*args, **kwargs)
            duration = time.time() - start
            self.logger.debug(f"Finished `{fn.__name__}` in {duration:.2f} seconds")
            return result
        return wrapper
