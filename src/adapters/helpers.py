import asyncio
from typing import Any, Coroutine

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

AdapterSession = AsyncSession


def run_after_commit(session: AsyncSession, func: Coroutine[Any, Any, Any]) -> None:
    return event.listen(
        target=session.sync_session,
        identifier="after_commit",
        fn=lambda _: asyncio.create_task(func),  # type: ignore
        once=True,
    )
