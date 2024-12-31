from src.domain.repositories.base_repository import BaseRepository
from src.domain.entities.employee import Employee

from abc import abstractmethod
from typing import List
import datetime

class EmployeeRepository(BaseRepository[Employee]):
    @abstractmethod
    async def find_by_department(self, department_id: int) -> List[Employee]:
        pass

    @abstractmethod
    async def find_by_job(self, job_id: int) -> List[Employee]:
        pass

    @abstractmethod
    async def find_by_hire_date_range(self, start_date: datetime, end_date: datetime) -> List[Employee]:
        pass