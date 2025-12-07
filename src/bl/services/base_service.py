from src.adapters.adapters_manager import AdaptersManager


class BaseService:
    def __init__(self, adapters_manager: AdaptersManager) -> None:
        self._adapters_manager = adapters_manager

    @property
    def adapters_manager(self) -> AdaptersManager:
        return self._adapters_manager
