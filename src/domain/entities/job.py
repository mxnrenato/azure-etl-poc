from dataclasses import dataclass


@dataclass
class Job:
    id: int
    name: str

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Job name cannot be empty")
        if self.id <= 0:
            raise ValueError("Job ID must be positive")
