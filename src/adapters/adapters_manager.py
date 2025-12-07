from src.adapters.managers.ip_address_adapter import IPAddressAdapter
from src.db.managers.db_manager import DBManager


class AdaptersManager:
    def __init__(self, db_manager: DBManager) -> None:
        self._ip_address_adapter = IPAddressAdapter(
            db_manager=db_manager,
        )

    @property
    def ip_adapter(self) -> IPAddressAdapter:
        return self._ip_address_adapter
