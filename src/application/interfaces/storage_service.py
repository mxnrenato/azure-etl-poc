from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    @abstractmethod
    async def store_file(self, file_content: BinaryIO, filename: str) -> bool:
        pass

    @abstractmethod
    async def retrieve_file(self, filename: str) -> BinaryIO:
        pass
