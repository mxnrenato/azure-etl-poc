from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class HireDate:
    value: datetime

    def __post_init__(self):
        if not isinstance(self.value, datetime):
            raise ValueError("Hire date must be a datetime object")
        if self.value > datetime.now():
            raise ValueError("Hire date cannot be in the future")