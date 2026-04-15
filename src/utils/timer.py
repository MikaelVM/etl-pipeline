from time import time
from .logger import setup_logger


def timer(func):
    """A decorator that measures the execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(f"Execution time: {end_time - start_time:.4f} seconds")
        return result
    return wrapper