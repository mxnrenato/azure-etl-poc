from src.domain.repositories.base_repository import BaseRepository
from src.domain.entities.job import Job

from abc import abstractmethod
from typing import Optional


class JobRepository(BaseRepository[Job]):
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Job]:
        pass
