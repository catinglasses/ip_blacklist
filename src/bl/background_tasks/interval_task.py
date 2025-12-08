import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

class IntervalTask:
    def __init__(
        self,
        name: str,
        period: float,
        func: Callable[..., Awaitable[None]],
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        self._name = name
        self._period = period
        self._func = func
        self._kwargs = kwargs

        self._asyncio_task: asyncio.Task[None] | None = None
        self._sleep_task: asyncio.Task[None] | None = None
        self._is_stopped = True

        self._last_log: datetime | None = None

    def start(self) -> None:
        if self._asyncio_task is not None or not self._is_stopped:
            raise RuntimeError('Can\'t stop task if it already started')

        self._asyncio_task = asyncio.create_task(self._run())
        self._is_stopped = False

    async def stop(self) -> None:
        if self._asyncio_task is None or self._is_stopped:
            raise RuntimeError('Can\'t stop task if it isn\'t running')

        self._is_stopped = True
        self._asyncio_task.cancel()

        await asyncio.wait([self._asyncio_task])
        self._asyncio_task = None

    async def _run(self) -> None:
        try:
            while not self._is_stopped:
                try:
                    if self._last_log is None or self._last_log + timedelta(minutes=10) < datetime.now():
                        logger.info(f'run interval task {self._name}')
                        self._last_log = datetime.now()

                    await self._func(**self._kwargs)

                except asyncio.CancelledError:
                    logger.info(f'interval task {self._name} cancelled')
                    return

                except Exception:
                    logger.exception(f'interval task {self._name} failed')

                await asyncio.sleep(self._period)

        except asyncio.CancelledError:
            logger.info(f'interval task {self._name} cancelled')
            return
