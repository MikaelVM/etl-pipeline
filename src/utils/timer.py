"""Utility module that provides a decorator to measure the execution time of functions."""
from collections.abc import Callable
from functools import wraps
from time import time
from typing import ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')


def timer(func: Callable[P, R]) -> Callable[P, R]:
    """Measure the execution time of a function.

    Args:
        func (Callable): The function whose execution time is to be measured.
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """Measure the execution time of the wrapped function and print it.

        Args:
            args: Positional arguments to be passed to the wrapped function.
            kwargs: Keyword arguments to be passed to the wrapped function.
        """
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()

        print(f"Execution time: {end_time - start_time:.4f} seconds")

        return result

    return wrapper
