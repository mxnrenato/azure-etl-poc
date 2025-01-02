from dataclasses import dataclass
from datetime import datetime


@dataclass
class Employee:
    id: int
    name: str
    hire_datetime: datetime
    department_id: int
    job_id: int

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Employee name cannot be empty")
        if self.id <= 0:
            raise ValueError("Employee ID must be positive")
        if self.department_id <= 0:
            raise ValueError("Department ID must be positive")
        if self.job_id <= 0:
            raise ValueError("Job ID must be positive")
