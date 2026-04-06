"""Simple retry helper for flaky operations."""

import time
from typing import Callable, Type, TypeVar

T = TypeVar("T")


def retry_on_exception(func: Callable[[], T], exceptions: tuple[Type[BaseException], ...], retries: int = 2, delay: float = 1.0) -> T:
    """Retry ``func`` when it raises one of ``exceptions``.

    Returns the function result or re-raises the last captured exception after
    exhausting retries. Useful for stabilizing transient Appium actions.
    """

    last_err: BaseException | None = None
    for attempt in range(retries + 1):
        try:
            return func()
        except exceptions as err:  # noqa: PERF203
            last_err = err
            if attempt == retries:
                break
            time.sleep(delay)
    raise last_err  # type: ignore[misc]  # last_err cannot be None here


__all__ = ["retry_on_exception"]
