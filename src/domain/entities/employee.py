from dataclasses import dataclass
from datetime import datetime


from dataclasses import dataclass
from datetime import datetime


@dataclass
class Employee:
    id: int
    name: str
    hire_datetime: datetime
    department_id: int = -1
    job_id: int = -1

    def __post_init__(self):
        if self.name is None or not self.name.strip():
            raise ValueError("Employee name cannot be empty or None")
        if self.id <= 0:
            raise ValueError("Employee ID must be positive")
        if self.department_id <= 0:
            print("Warning: Department ID is invalid, setting to default (-1).")
        if self.job_id <= 0:
            print("Warning: Job ID is invalid, setting to default (-1).")
