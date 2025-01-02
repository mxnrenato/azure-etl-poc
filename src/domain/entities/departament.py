from dataclasses import dataclass


@dataclass
class Department:
    id: int
    name: str

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Department name cannot be empty")
        if self.id <= 0:
            raise ValueError("Department ID must be positive")
