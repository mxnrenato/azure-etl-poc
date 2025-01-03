from dataclasses import dataclass


@dataclass
class Department:
    id: int
    department: str  # Cambiado de 'name' a 'department'

    def __post_init__(self):
        if not self.department.strip():  # Validar el nuevo nombre 'department'
            raise ValueError("Department name cannot be empty")
        if self.id <= 0:
            raise ValueError("Department ID must be positive")
