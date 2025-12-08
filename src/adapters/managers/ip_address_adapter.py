import logging
from datetime import datetime

from sqlalchemy.ext.asyncio.session import _AsyncSessionContextManager  # type: ignore

from settings import DEFAULT_TTL, IP_COOLING_PERIOD
from src.adapters.helpers import AdapterSession
from src.common.enums import IPStatus
from src.db.managers.db_manager import DBManager
from src.db.models import IPAddress

logger = logging.getLogger(__name__)


class IPAddressAdapter:
    def __init__(self, db_manager: DBManager) -> None:
        self._db_manager = db_manager

    def init_adapter_session(self) -> _AsyncSessionContextManager[AdapterSession]:
        return self._db_manager.session()

    async def get_ip_by_address(
        self,
        ip: str,
        adapter_session: AdapterSession | None = None,
    ) -> IPAddress | None:
        try:
            return await self._db_manager.ip_manager.get_ip_address(
                ip=ip,
                current_session=adapter_session,
            )
        except Exception as e:
            logger.error(f"Error getting IP {ip}: {e}")
            raise

    async def create_ip(
        self,
        ip: str,
        status: IPStatus,
        ttl: int | None,
        description: str | None = None,
        expires_at: datetime | None = None,
        last_blacklist_at: datetime | None = None,
        adapter_session: AdapterSession | None = None,
    ) -> IPAddress | None:
        try:
            return await self._db_manager.ip_manager.upsert_ip_address(
                ip=ip,
                status=status,
                ttl=ttl or DEFAULT_TTL,
                description=description,
                expires_at=expires_at,
                last_blacklist_at=last_blacklist_at,
                current_session=adapter_session,
            )
        except Exception as e:
            logger.error(f"Error creating IP {ip}: {e}")
            raise

    async def update_ip(
        self,
        ip: str,
        status: IPStatus | None = None,
        description: str | None = None,
        expires_at: datetime | None = None,
        last_blacklist_at: datetime | None = None,
        adapter_session: AdapterSession | None = None,
    ) -> IPAddress | None:
        try:
            return await self._db_manager.ip_manager.patch_ip_address(
                ip=ip,
                status=status,
                description=description,
                expires_at=expires_at,
                last_blacklist_at=last_blacklist_at,
                current_session=adapter_session,
            )
        except Exception as e:
            logger.error(f"Error updating IP {ip}: {e}")
            raise

    async def delete_ip(
        self,
        ip: str,
        adapter_session: AdapterSession | None = None,
    ) -> None:
        try:
            await self._db_manager.ip_manager.delete_ip_address(
                ip=ip,
                current_session=adapter_session,
            )
        except Exception as e:
            logger.error(f"Error deleting IP {ip}: {e}")
            raise

    async def get_blacklisted_ips(
        self,
        adapter_session: AdapterSession | None = None,
    ) -> list[str]:
        try:
            return await self._db_manager.ip_manager.get_blacklisted_ip_addresses(
                current_session=adapter_session,
            )
        except Exception as e:
            logger.error(f"Error getting blacklisted IPs: {e}")
            raise

    async def archive_ip(
        self,
        adapter_session: AdapterSession | None = None,
    ) -> bool:
        try:
            ip_to_archive = await self._db_manager.ip_manager.get_blacklisted_ip_to_archive(
                cooling_period=IP_COOLING_PERIOD,
                current_session=adapter_session,
            )

            if not ip_to_archive:
                return False

            archived_ip = await self._db_manager.ip_manager.patch_ip_address(
                id=ip_to_archive.id,
                status=IPStatus.ARCHIVED,
                current_session=adapter_session,
            )

            return archived_ip is not None

        except Exception as e:
            logger.error(f'Error archiving IP: {e}')
            return False

    async def delete_expired_ip(
        self,
        adapter_session: AdapterSession | None = None,
    ) -> bool:
        try:
            ip_to_delete = await self._db_manager.ip_manager.get_expired_ip_to_delete(
                current_session=adapter_session,
            )

            if not ip_to_delete:
                return False

            await self._db_manager.ip_manager.delete_ip_address(
                id=ip_to_delete.id,
                current_session=adapter_session,
            )
            return True

        except Exception as e:
            logger.error(f'Error deleting expired IP: {e}')
            return False

    async def check_ip_exists(
        self,
        ip: str,
        adapter_session: AdapterSession | None = None,
    ) -> bool:
        try:
            result = await self._db_manager.ip_manager.get_ip_address(
                ip=ip,
                current_session=adapter_session,
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error checking IP existence {ip}: {e}")
            raise
