from src.domain.entities.employee import Employee
from src.domain.repositories.employee_repository import EmployeeRepository
from src.application.interfaces.storage_service import StorageService
from src.application.dto.employee_dto import BatchIngestDTO
from src.domain.exceptions.domain_exceptions import IngestError

from typing import BinaryIO
import pandas as pd
from datetime import datetime
from io import StringIO
import logging

logger = logging.getLogger(__name__)


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
            file_content.seek(0)  # Reiniciar el cursor
            employees, invalid_rows = self._process_file(file_content)

            # Log invalid rows
            if invalid_rows:
                logger.warning(f"Invalid rows: {len(invalid_rows)}")

            # Store valid records
            results = await self.employee_repository.save_batch(employees)

            return {
                "processed": len(employees) + len(invalid_rows),
                "successful": sum(1 for r in results if r),
                "failed": len(invalid_rows) + sum(1 for r in results if not r),
                "invalid_rows": len(invalid_rows),
            }
        except Exception as e:
            logger.error(f"Error during ingestion: {str(e)}")
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
            logger.error(f"Error during batch ingestion: {str(e)}")
            raise IngestError(f"Error during batch ingestion: {str(e)}")

    def _process_file(
        self, file_content: BinaryIO
    ) -> tuple[list[Employee], list[dict]]:
        """Process and validate employee data from CSV file"""
        try:
            # Leer archivo CSV
            file_content.seek(0)  # Asegurarse de leer desde el inicio
            df = pd.read_csv(StringIO(file_content.read().decode("utf-8")))

            # Validar columnas obligatorias
            required_columns = ["id", "name", "datetime", "department_id", "job_id"]
            if not all(col in df.columns for col in required_columns):
                raise ValueError(
                    "Archivo CSV no contiene todas las columnas requeridas"
                )

            # Validar filas y crear objetos Employee
            employees = []
            invalid_rows = []

            for _, row in df.iterrows():
                try:
                    # Validar que todos los campos sean requeridos y correctos
                    if (
                        (
                            pd.isnull(row["id"])
                            or not isinstance(row["id"], (int, float))
                        )
                        or (
                            pd.isnull(row["name"])
                            or not isinstance(row["name"], str)
                            or not row["name"].strip()
                        )
                        or (
                            pd.isnull(row["datetime"])
                            or not isinstance(row["datetime"], str)
                        )
                        or (
                            pd.isnull(row["department_id"])
                            or not isinstance(row["department_id"], (int, float))
                        )
                        or (
                            pd.isnull(row["job_id"])
                            or not isinstance(row["job_id"], (int, float))
                        )
                    ):
                        raise ValueError("Invalid or missing fields in row")

                    # Convert and sanitize fields
                    id_value = int(row["id"])
                    name_value = row["name"].strip()
                    datetime_value = datetime.fromisoformat(
                        row["datetime"].replace("Z", "")
                    )
                    department_id_value = int(row["department_id"])
                    job_id_value = int(row["job_id"])

                    employees.append(
                        Employee(
                            id=id_value,
                            name=name_value,
                            hire_datetime=datetime_value,
                            department_id=department_id_value,
                            job_id=job_id_value,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Invalid row skipped: {row}. Error: {str(e)}")
                    invalid_rows.append(row.to_dict())

            return employees, invalid_rows
        except Exception as e:
            raise ValueError(f"Error al procesar el archivo: {str(e)}")
