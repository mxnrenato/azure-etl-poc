from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def save(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def save_batch(self, entities: List[T]) -> List[bool]:
        pass

    @abstractmethod
    async def backup(self, format: str = "AVRO") -> str:
        pass

    @abstractmethod
    async def restore(self, backup_path: str) -> bool:
        pass
