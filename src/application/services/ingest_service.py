from domain.entities.employee import Employee
from domain.repositories.employee_repository import EmployeeRepository
from application.interfaces.storage_service import StorageService
from application.dto.employee_dto import BatchIngestDTO
from domain.exceptions.domain_exceptions import IngestError

from typing import BinaryIO


class IngestService:
    def __init__(
        self, employee_repository: EmployeeRepository, storage_service: StorageService
    ):
        self.employee_repository = employee_repository
        self.storage_service = storage_service

    async def ingest_employees_file(
        self, file_content: BinaryIO, filename: str
    ) -> dict:
        """Process and store employee data from file"""
        try:
            # Store raw file
            await self.storage_service.store_file(file_content, f"raw/{filename}")

            # Process and validate data
            employees = self._process_file(file_content)

            # Store valid records
            results = await self.employee_repository.save_batch(employees)

            return {
                "processed": len(employees),
                "successful": sum(1 for r in results if r),
                "failed": sum(1 for r in results if not r),
            }
        except Exception as e:
            raise IngestError(f"Error during ingestion: {str(e)}")

    async def ingest_batch(self, batch_dto: BatchIngestDTO) -> dict:
        """Process batch of employee records"""
        try:
            employees = [
                Employee(
                    id=emp.id,
                    name=emp.name,
                    hire_datetime=emp.hire_datetime,
                    department_id=emp.department_id,
                    job_id=emp.job_id,
                )
                for emp in batch_dto.employees
            ]

            results = await self.employee_repository.save_batch(employees)

            return {
                "processed": len(employees),
                "successful": sum(1 for r in results if r),
                "failed": sum(1 for r in results if not r),
            }
        except Exception as e:
            raise IngestError(f"Error during batch ingestion: {str(e)}")
