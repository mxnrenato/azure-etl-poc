from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Logger(ABC):
    @abstractmethod
    async def info(self, message: str, **kwargs: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def error(
        self, message: str, error: Optional[Exception] = None, **kwargs: Dict[str, Any]
    ) -> None:
        pass

    @abstractmethod
    async def warning(self, message: str, **kwargs: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def debug(self, message: str, **kwargs: Dict[str, Any]) -> None:
        pass
