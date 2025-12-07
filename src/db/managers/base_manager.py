from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio.session import (
    _AsyncSessionContextManager,  # type: ignore
    async_sessionmaker,
)
from sqlalchemy.orm import close_all_sessions


class BaseDBManager:
    def __init__(self, async_engine: AsyncEngine) -> None:
        self._async_engine = async_engine
        self._async_session = async_sessionmaker(
            bind=self._async_engine,
            expire_on_commit=False,
        )

    def session(self) -> _AsyncSessionContextManager[AsyncSession]:
        return self._async_session.begin()

    @asynccontextmanager
    async def _manage_async_session(
        self,
        current_session: AsyncSession | None = None,
    ) -> AsyncIterator[AsyncSession]:
        async with AsyncExitStack() as stack:
            if current_session is None:
                session = await stack.enter_async_context(self._async_session())
            else:
                session = current_session

            try:
                yield session

            except Exception:
                await session.rollback()
                raise

            else:
                await session.commit()

    @asynccontextmanager
    async def use_or_create_session(
        self,
        current_session: AsyncSession | None = None,
    ) -> AsyncIterator[AsyncSession]:
        async with self._manage_async_session(current_session) as session:
            yield session

    async def close(self) -> None:
        close_all_sessions()
        await self._async_engine.dispose()
