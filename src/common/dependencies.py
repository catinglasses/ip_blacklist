from typing import AsyncGenerator

from fastapi import Depends

import settings
from src.adapters.adapters_manager import AdaptersManager
from src.bl.bl_manager import BLManager
from src.db.managers.db_manager import DBManager, init_db_manager


async def get_db_manager() -> AsyncGenerator[DBManager, None]:
    db_manager = await init_db_manager(
        db_connection_url=settings.DATABASE_URL,
        run_migrations=True,
    )

    try:
        yield db_manager
    finally:
        await db_manager.close()


async def get_adapters_manager(
    db_manager: DBManager = Depends(get_db_manager),
) -> AdaptersManager:
    return AdaptersManager(db_manager=db_manager)


async def get_bl_manager(
    adapters_manager: AdaptersManager = Depends(get_adapters_manager),
) -> BLManager:
    return BLManager(adapters_manager=adapters_manager)
