"""Measure elapsed time and enforce time budgets on async operations."""

import functools
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from types import TracebackType
from typing import ParamSpec, TypeVar

from ..services.logger import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class BudgetExceededError(Exception):
    """An operation took longer than its time budget."""


class PerformanceTimer:
    """Time a block of code; works as a sync or async context manager.

    ``elapsed_ms`` is set on exit and logged at ``log_level`` under ``operation_name``.
    """

    def __init__(self, operation_name: str, log_level: str = "info") -> None:
        self.operation_name = operation_name
        self.log_level = log_level.lower()
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.elapsed_ms: float = 0.0

    def _start(self) -> None:
        self.start_time = time.perf_counter()

    def _stop(self) -> None:
        self.end_time = time.perf_counter()
        self.elapsed_ms = (self.end_time - (self.start_time or self.end_time)) * 1000
        log_fn: Callable[..., None] = getattr(logger, self.log_level)
        log_fn(
            f"Operation completed: {self.operation_name}",
            operation=self.operation_name,
            duration_ms=self.elapsed_ms,
        )

    def __enter__(self) -> "PerformanceTimer":
        self._start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._stop()

    async def __aenter__(self) -> "PerformanceTimer":
        self._start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._stop()

    def checkpoint(self, name: str) -> float:
        """Log and return milliseconds elapsed since the timer started (0 if not started)."""
        elapsed = (time.perf_counter() - self.start_time) * 1000 if self.start_time else 0.0
        logger.debug(
            f"Timer checkpoint: {name}",
            operation=self.operation_name,
            checkpoint=name,
            elapsed_ms=elapsed,
        )
        return elapsed


def enforce_budget(
    budget_ms: float,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorate an async function so it raises ``BudgetExceededError`` when it runs too long.

    The function runs to completion; the budget is checked after, not by cancellation.
    """

    def decorator(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.perf_counter()
            try:
                result = await fn(*args, **kwargs)
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    "Operation failed", function=fn.__name__, elapsed_ms=elapsed_ms, error=str(exc)
                )
                raise
            elapsed_ms = (time.perf_counter() - start) * 1000
            if elapsed_ms > budget_ms:
                logger.warning(
                    "Operation exceeded budget",
                    function=fn.__name__,
                    budget_ms=budget_ms,
                    actual_ms=elapsed_ms,
                )
                raise BudgetExceededError(
                    f"{fn.__name__} exceeded budget of {budget_ms}ms (took {elapsed_ms:.1f}ms)"
                )
            logger.debug(
                "Operation within budget",
                function=fn.__name__,
                budget_ms=budget_ms,
                actual_ms=elapsed_ms,
            )
            return result

        return wrapper

    return decorator


@asynccontextmanager
async def time_budget(budget_ms: float, operation_name: str) -> AsyncIterator[PerformanceTimer]:
    """Time a block and raise ``BudgetExceededError`` on exit if it overran ``budget_ms``."""
    timer = PerformanceTimer(operation_name)
    async with timer:
        yield timer
    if timer.elapsed_ms > budget_ms:
        raise BudgetExceededError(
            f"{operation_name} exceeded budget of {budget_ms}ms (took {timer.elapsed_ms:.1f}ms)"
        )
