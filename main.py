import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

import settings
from src.api.router import api_router
from src.bl.background_tasks.archive_ip_task import run_archive_ip_task
from src.bl.background_tasks.cleanup_task import run_cleanup_ip_task
from src.bl.background_tasks.interval_task import IntervalTask

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    logger.info("Starting up...")

    archive_interval_task, cleanup_interval_task = startup_background_tasks()

    yield

    logger.info("Shutting down...")

    await shutdown_background_tasks(archive_interval_task, cleanup_interval_task)

def startup_background_tasks() -> tuple[IntervalTask, IntervalTask]:
    logger.info('starting archive interval task...')
    archive_interval_task = IntervalTask(
        name='archive_ips',
        period=settings.ARCHIVE_CHECK_PERIOD,
        func=run_archive_ip_task,
    )
    archive_interval_task.start()
    logger.info('archive interval task started successfully.')

    logger.info('starting cleanup interval task...')
    cleanup_interval_task = IntervalTask(
        name='cleanup_expired_ips',
        period=settings.CLEANUP_PERIOD,
        func=run_cleanup_ip_task,
    )
    cleanup_interval_task.start()
    logger.info('cleanup interval task started successfully.')
    return archive_interval_task,cleanup_interval_task

async def shutdown_background_tasks(
    archive_interval_task: IntervalTask,
    cleanup_interval_task: IntervalTask,
) -> None:
    if cleanup_interval_task:
        logger.info('Shutting down cleanup interval task...')
        await cleanup_interval_task.stop()
        logger.info('Cleanup interval task shutdown.')

    if archive_interval_task:
        logger.info('Shutting down archive interval task...')
        await archive_interval_task.stop()
        logger.info('Archive interval task shutdown.')

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

@app.get('/')
async def root() -> dict[str, Any]:
    return {'message': 'IP Blacklist Service'}
