from src.adapters.adapters_manager import AdaptersManager
from src.bl.services.ip_address_service import IPAddressService


class BLManager:
    def __init__(self, adapters_manager: AdaptersManager) -> None:
        self._ip_service = IPAddressService(adapters_manager=adapters_manager)

    @property
    def ip_service(self) -> IPAddressService:
        return self._ip_service
