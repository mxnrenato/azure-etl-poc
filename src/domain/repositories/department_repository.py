from src.domain.repositories.base_repository import BaseRepository
from src.domain.entities.departament import Department

from abc import abstractmethod
from typing import Optional


class DepartmentRepository(BaseRepository[Department]):
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Department]:
        pass
