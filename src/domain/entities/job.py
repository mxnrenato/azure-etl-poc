from dataclasses import dataclass


@dataclass
class Job:
    id: int
    job: str  # Cambiado de 'name' a 'job'

    def __post_init__(self):
        if not self.job.strip():  # Validar el nuevo nombre 'job'
            raise ValueError("Job name cannot be empty")
        if self.id <= 0:
            raise ValueError("Job ID must be positive")