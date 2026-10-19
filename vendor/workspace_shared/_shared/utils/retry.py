"""Retry an async callable with exponential backoff and optional jitter."""

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from ..services.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


async def retry(
    fn: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay_s: float = 1.0,
    max_delay_s: float = 30.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Call ``fn`` until it succeeds or ``max_attempts`` is reached.

    The delay before attempt ``n`` is ``min(base_delay_s * 2**(n-2), max_delay_s)``, scaled by a
    random factor in ``[0.5, 1.5)`` when ``jitter`` is on.

    Raises:
        ValueError: ``max_attempts`` is less than 1.
        Exception: The last exception raised by ``fn`` once attempts are exhausted. Exceptions
            not in ``retryable_exceptions`` propagate immediately.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    name = getattr(fn, "__name__", repr(fn))

    for attempt in range(1, max_attempts + 1):
        try:
            result = await fn()
        except retryable_exceptions as exc:
            if attempt >= max_attempts:
                logger.error(
                    "All retry attempts exhausted",
                    function=name,
                    attempts=max_attempts,
                    last_error=str(exc),
                )
                raise
            delay = min(base_delay_s * (2 ** (attempt - 1)), max_delay_s)
            if jitter:
                delay *= 0.5 + random.random()
            logger.warning(
                "Retry attempt failed, backing off",
                function=name,
                attempt=attempt,
                max_attempts=max_attempts,
                delay_s=delay,
                error=str(exc),
            )
            await asyncio.sleep(delay)
        else:
            if attempt > 1:
                logger.info("Retry succeeded", attempt=attempt, function=name)
            return result

    raise AssertionError("unreachable: loop returns or raises")  # pragma: no cover
