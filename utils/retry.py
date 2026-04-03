"""Simple retry helper for flaky operations."""

import time
from typing import Callable, Type


def retry_on_exception(func: Callable, exceptions: tuple[Type[BaseException], ...], retries: int = 2, delay: float = 1.0):
    """Retry a callable on given exceptions."""

    last_err = None
    for attempt in range(retries + 1):
        try:
            return func()
        except exceptions as err:  # noqa: PERF203
            last_err = err
            if attempt == retries:
                break
            time.sleep(delay)
    raise last_err


__all__ = ["retry_on_exception"]
