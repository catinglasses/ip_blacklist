import logging

from fastapi import Depends

from src.adapters.adapters_manager import AdaptersManager
from src.common.dependencies import get_adapters_manager

logger = logging.getLogger(__name__)


async def run_archive_ip_task(
    adapters_manager: AdaptersManager = Depends(get_adapters_manager),
) -> None:  # pragma: no cover
    while True:
        processed = await get_and_process_archive_ip_task(
            adapters_manager=adapters_manager,
        )
        if not processed:
            return


async def get_and_process_archive_ip_task(adapters_manager: AdaptersManager) -> bool:
    try:
        async with adapters_manager.ip_adapter.init_adapter_session() as session:
            return await adapters_manager.ip_adapter.archive_ip(adapter_session=session)

    except Exception as e:
        logger.exception(f'Exception occured during archive ip task execution: {e}')
        return False
