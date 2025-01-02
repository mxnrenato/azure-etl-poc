from pydantic import BaseModel
from datetime import datetime
from typing import List


class EmployeeDTO(BaseModel):
    id: int
    name: str
    hire_datetime: datetime
    department_id: int
    job_id: int


class BatchIngestDTO(BaseModel):
    employees: List[EmployeeDTO]
