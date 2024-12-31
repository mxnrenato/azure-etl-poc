from typing import List

class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class EntityNotFoundError(DomainException):
    """Raised when an entity is not found"""
    pass

class ValidationError(DomainException):
    """Raised when entity validation fails"""
    pass

class BatchOperationError(DomainException):
    """Raised when a batch operation fails"""
    def __init__(self, message: str, failed_indices: List[int]):
        super().__init__(message)
        self.failed_indices = failed_indices

class BackupError(DomainException):
    """Raised when backup operation fails"""
    pass

class RestoreError(DomainException):
    """Raised when restore operation fails"""
    pass