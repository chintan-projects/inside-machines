"""Durable production queue subscriber and explicit local development worker."""

import asyncio

from _shared.services.logger import get_logger
from vercel.queue import send, subscribe

from .assets import Assets
from .pipeline import Pipeline
from .provider import configure_gateway
from .settings import load_settings
from .store import Store

_local_tasks: set[asyncio.Task[None]] = set()
logger = get_logger(__name__)


def _finished(task: asyncio.Task[None]) -> None:
    _local_tasks.discard(task)
    if not task.cancelled() and task.exception() is not None:
        logger.error(
            "Local worker stopped before completing its delivery", error_type=type(task.exception()).__name__
        )


async def enqueue_job(job_id: str, phase: str) -> None:
    """Production uses Vercel Queues; local tasks are explicitly non-durable."""
    config = load_settings()
    if config.production:
        await send("inside-lessons", {"job_id": job_id}, idempotency_key=f"{job_id}:{phase}")
    else:
        task = asyncio.create_task(consume({"job_id": job_id}))
        _local_tasks.add(task)
        task.add_done_callback(_finished)


@subscribe(
    topic="inside-lessons", max_concurrency=1, max_attempts=5, retry_after=load_settings().lease_seconds + 15
)
async def consume(payload: dict[str, str]) -> None:
    """Use checkpointed phases to keep each invocation inside function limits."""
    config = load_settings()
    configure_gateway(config)
    pipeline = Pipeline(Store(config.database_url, config.data_dir), config, Assets(config), enqueue_job)
    await pipeline.run(payload["job_id"])
