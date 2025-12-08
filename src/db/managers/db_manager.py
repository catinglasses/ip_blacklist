import logging

from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import Connection, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

import settings
from src.db.managers.base_manager import BaseDBManager
from src.db.managers.ip_address_manager import IPAddressDBManager

logger = logging.getLogger(__name__)


class DBManager(BaseDBManager):
    def __init__(self, async_engine: AsyncEngine) -> None:
        super().__init__(async_engine)
        self._ip_address_manager = IPAddressDBManager(async_engine)

    @property
    def ip_manager(self) -> IPAddressDBManager:
        return self._ip_address_manager

    async def healthcheck(self) -> bool:
        try:
            async with self.session() as session:
                await session.execute(
                    text("CREATE TEMP TABLE healthcheck (id SERIAL PRIMARY KEY)")
                )
                await session.execute(text("DROP TABLE healthcheck"))
                return True

        except Exception:
            logger.exception("db healthcheck failed")
            return False


async def init_db_manager(
    db_connection_url: str,
) -> DBManager:
    engine = create_async_engine(
        url=db_connection_url,
        pool_pre_ping=True,
        pool_size=settings.DB_MAX_CONNECTIONS,
    )

    return DBManager(async_engine=engine)
