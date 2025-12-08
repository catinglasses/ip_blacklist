import logging
from datetime import datetime, timedelta

import settings
from src.adapters.adapters_manager import AdaptersManager
from src.api.exceptions import (
    DuplicateIPException,
    InvalidTTLException,
    IPNotFoundException,
)
from src.api.schema import IPAddressCreate, IPAddressResponse
from src.bl.services.base_service import BaseService
from src.common.enums import IPStatus

logger = logging.getLogger(__name__)


class IPAddressService(BaseService):
    def __init__(self, adapters_manager: AdaptersManager) -> None:
        super().__init__(adapters_manager)

    async def _calculate_expires_at(
        self,
        ttl_days: int | None = None,
    ) -> datetime:
        if ttl_days is None:
            return datetime.now() + timedelta(days=settings.DEFAULT_TTL + settings.IP_COOLING_PERIOD)

        if not (1 <= ttl_days <= 365):
            raise InvalidTTLException()

        return datetime.now() + timedelta(days=ttl_days + settings.IP_COOLING_PERIOD)

    async def add_ip_address(self, ip_data: IPAddressCreate) -> IPAddressResponse:
        if await self.adapters_manager.ip_adapter.check_ip_exists(ip=ip_data.ip):
            raise DuplicateIPException()

        expires_at = await self._calculate_expires_at(
            ttl_days=ip_data.ttl,
        )

        new_ip = await self.adapters_manager.ip_adapter.create_ip(
            ip=ip_data.ip,
            status=ip_data.status,
            ttl=ip_data.ttl,
            description=ip_data.description,
            expires_at=expires_at,
            last_blacklist_at=datetime.now(),
        )

        assert new_ip is not None

        return IPAddressResponse(
            id=new_ip.id,
            status=new_ip.status,
            created_at=new_ip.created_at,
            updated_at=new_ip.updated_at,
            last_blacklist_at=new_ip.last_blacklist_at,
        )

    async def get_blacklisted_ips(self) -> list[str]:
        return await self.adapters_manager.ip_adapter.get_blacklisted_ips()

    async def reblacklist_ip(self, ip: str, reason: str | None) -> IPAddressResponse:
        ip_address = await self.adapters_manager.ip_adapter.get_ip_by_address(ip=ip)

        if not ip_address:
            raise IPNotFoundException

        if ip_address.status != IPStatus.ARCHIVED:
            logger.info(f"No need to re-blacklist {ip=}: {ip_address.status=}")
            return IPAddressResponse(
                id=ip_address.id,
                status=ip_address.status,
                created_at=ip_address.created_at,
                updated_at=ip_address.updated_at,
                last_blacklist_at=ip_address.last_blacklist_at,
            )

        updated_ip_address = await self.adapters_manager.ip_adapter.update_ip(
            ip=ip,
            status=IPStatus.BLACKLIST,
            last_blacklist_at=datetime.now(),
            description=(
                f"Re-blacklisted at {datetime.now().date()}: {reason}\n"
                f"Previous description: {ip_address.description or None}"
            ),
            expires_at=await self._calculate_expires_at(
                ttl_days=settings.REPEATED_BLACKLIST_IP_TTL,
            ),
        )

        assert updated_ip_address is not None

        return IPAddressResponse(
            id=updated_ip_address.id,
            status=updated_ip_address.status,
            created_at=updated_ip_address.created_at,
            updated_at=updated_ip_address.updated_at,
            last_blacklist_at=updated_ip_address.last_blacklist_at,
        )
