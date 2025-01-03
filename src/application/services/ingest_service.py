from src.domain.entities.employee import Employee
from src.domain.entities.departament import Department
from src.domain.entities.job import Job
from src.domain.repositories.employee_repository import EmployeeRepository
from src.domain.repositories.department_repository import DepartmentRepository
from src.domain.repositories.job_repository import JobRepository
from src.application.interfaces.storage_service import StorageService
from src.application.dto.employee_dto import BatchIngestDTO
from src.domain.exceptions.domain_exceptions import IngestError
import requests
from typing import BinaryIO, List, Dict, Tuple
import pandas as pd
from datetime import datetime
from io import StringIO
import logging

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(
        self, employee_repository: EmployeeRepository, department_repository: DepartmentRepository, job_repository: JobRepository,storage_service: StorageService
    ):
        self.employee_repository = employee_repository
        self.department_repository = department_repository
        self.job_repository = job_repository
        self.storage_service = storage_service

    async def process_and_store_file_in_batches(
        self, 
        file_content: BinaryIO, 
        table_name: str,
        batch_size: int = 1000
    ) -> Dict:
        """
        Process and store data from a file into the database using batch processing.
        
        Args:
            file_content: The file content to process
            table_name: The name of the table to store the data
            batch_size: Number of records to process in each batch
        """
        try:
            # Store the raw file in blob storage
            filename = f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            is_stored = await self.storage_service.store_file(file_content, filename)
            
            if not is_stored:
                raise IngestError("Failed to store file in Blob Storage")
            
            logger.info(f"File stored in Blob Storage: {filename}")

            # Define required columns for each table
            required_columns_by_table = {
                "employees": ["id", "name", "datetime", "department_id", "job_id"],
                "departments": ["id", "department"],
                "jobs": ["id", "job"]
            }

            if table_name not in required_columns_by_table:
                raise ValueError(f"Unknown table: {table_name}")

            # Reset file pointer
            file_content.seek(0)
            
            # Read CSV in chunks, explicitly setting the column names
            df_iterator = pd.read_csv(
                StringIO(file_content.read().decode('utf-8')),
                chunksize=batch_size,
                names=required_columns_by_table[table_name],  # Explicitly set column names
                header=None  # Indicate no header row in CSV
            )

            total_processed = 0
            total_successful = 0
            total_failed = 0
            total_invalid = 0

            # Process each batch
            for chunk in df_iterator:
                batch_records, invalid_rows = self._process_batch(chunk, table_name)
                
                # Save batch according to table type
                if batch_records:
                    if table_name == "employees":
                        save_results = await self.employee_repository.save_batch(batch_records)
                    elif table_name == "departments":
                        save_results = await self.department_repository.save_batch(batch_records)
                    elif table_name == "jobs":
                        save_results = await self.job_repository.save_batch(batch_records)
                    
                    successful = sum(1 for r in save_results if r)
                    failed = len(batch_records) - successful
                    
                    total_processed += len(batch_records) + len(invalid_rows)
                    total_successful += successful
                    total_failed += failed
                    total_invalid += len(invalid_rows)
                    
                    logger.info(
                        f"Batch processed - Success: {successful}, "
                        f"Failed: {failed}, Invalid: {len(invalid_rows)}"
                    )

            return {
                "processed": total_processed,
                "successful": total_successful,
                "failed": total_failed,
                "invalid_rows": total_invalid,
                "filename": filename
            }

        except Exception as e:
            logger.error(f"Error processing and storing file: {str(e)}")
            raise IngestError(f"Error processing and storing file: {str(e)}")

    def _process_batch(
        self, 
        batch_df: pd.DataFrame, 
        table_name: str
    ) -> Tuple[List[object], List[Dict]]:
        """
        Process a batch of records from the dataframe.
        """
        valid_records = []
        invalid_records = []

        # Ensure all required columns exist
        required_columns = {
            "employees": ["id", "name", "datetime", "department_id", "job_id"],
            "departments": ["id", "department"],
            "jobs": ["id", "job"]
        }.get(table_name)

        if not required_columns:
            raise ValueError(f"Unknown table: {table_name}")

        # Verify all required columns are present
        missing_columns = [col for col in required_columns if col not in batch_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Process each row in the batch
        for _, row in batch_df.iterrows():
            try:
                if table_name == "employees":
                    validated_data = self._validate_employee_row(row)
                    valid_records.append(Employee(**validated_data))
                elif table_name == "departments":
                    validated_data = self._validate_department_row(row)
                    valid_records.append(Department(**validated_data))
                elif table_name == "jobs":
                    validated_data = self._validate_job_row(row)
                    valid_records.append(Job(**validated_data))
            except ValueError as e:
                invalid_records.append(row.to_dict())
                logger.warning(f"Validation failed for row: {row.to_dict()}. Error: {str(e)}")

        return valid_records, invalid_records

    async def process_and_store_file(
        self, file_content: BinaryIO, table_name: str
    ) -> dict:
        """
        Process and store data from a file into the database.

        Args:
            file_content: The file content to process.
            table_name: The name of the table to store the data.

        Returns:
            A summary of the processing result.
        """
        try:
            # Store the raw file in blob storage
            is_stored = await self.storage_service.store_file(
                file_content, f"{table_name}.csv"
            )
            if not is_stored:
                raise IngestError("Failed to store the file in Blob Storage.")
            print(f"File stored in Blob Storage: {table_name}.csv")

            # Reset the file pointer and process the file
            file_content.seek(0)
            records, invalid_rows = self._process_file(file_content, table_name)

            # Log invalid rows
            if invalid_rows:
                print(
                    f"Found {len(invalid_rows)} invalid rows while processing '{table_name}'"
                )

            # Save valid records in the database
            if table_name == "employees":
                save_results = await self.employee_repository.save_batch(records)
                successful = sum(1 for r in save_results if r)
                failed = len(records) - successful
            elif table_name == "departments":
                save_results = await self.department_repository.save_batch(records)
                successful = sum(1 for r in save_results if r)
                failed = len(records) - successful
            elif table_name == "jobs":
                save_results = await self.job_repository.save_batch(records)
                successful = sum(1 for r in save_results if r)
                failed = len(records) - successful

            return {
                "processed": len(records) + len(invalid_rows),
                "successful": successful,
                "failed": failed + len(invalid_rows),
                "invalid_rows": len(invalid_rows),
            }
        except Exception as e:
            print(f"Error processing and storing file: {str(e)}")
            raise IngestError(f"Error processing and storing file: {str(e)}")

    async def ingest_employees_file(
        self, file_content: BinaryIO, filename: str
    ) -> dict:
        """Process and store employee data from file"""
        try:
            # Store raw file
            await self.storage_service.store_file(file_content, f"{filename}")

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
                    datetime=emp.datetime,
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
        self, file_content: BinaryIO, table_name: str
    ) -> tuple[List[object], List[Dict]]:
        """Process and validate data for the given table."""
        try:
            file_content.seek(0)

            # Define las columnas requeridas por tabla
            required_columns_by_table = {
                "employees": ["id", "name", "datetime", "department_id", "job_id"],
                "departments": ["id", "department"],
                "jobs": ["id", "job"]
            }

            if table_name not in required_columns_by_table:
                raise ValueError(f"Unknown table: {table_name}")

            required_columns = required_columns_by_table[table_name]

            # Leer el archivo CSV y asignar nombres de columnas si no existen
            df = pd.read_csv(
                StringIO(file_content.read().decode("utf-8")),
                names=required_columns,
                header=None,  # Indica que el CSV no tiene encabezados
            )

            # Verifica que todas las columnas requeridas estén presentes
            if not all(col in df.columns for col in required_columns):
                raise ValueError(
                    f"CSV file does not contain all required columns for table '{table_name}'"
                )

            valid_rows = []
            invalid_rows = []

            for _, row in df.iterrows():
                try:
                    # Validar y transformar según la tabla
                    if table_name == "employees":
                        employee_data = self._validate_employee_row(row)
                        valid_rows.append(Employee(**employee_data))
                    elif table_name == "departments":
                        department_data = self._validate_department_row(row)
                        valid_rows.append(Department(**department_data))  # Si tienes una clase para departamentos
                    elif table_name == "jobs":
                        job_data = self._validate_job_row(row)
                        valid_rows.append(Job(**job_data))  # Si tienes una clase para trabajos
                except ValueError as e:
                    invalid_rows.append(row.to_dict())
                    print(f"Validation failed for row: {row.to_dict()}. Error: {str(e)}")

            return valid_rows, invalid_rows
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")
        
    def _validate_employee_row(self, row: pd.Series) -> dict:
        """Validate and convert an employee row."""
        if pd.isnull(row["id"]) or not isinstance(row["id"], (int, float)) or row["id"] <= 0:
            raise ValueError("Invalid or missing 'id'")
        if pd.isnull(row["name"]) or not isinstance(row["name"], str) or not row["name"].strip():
            raise ValueError("Invalid or missing 'name'")
        if pd.isnull(row["datetime"]) or not isinstance(row["datetime"], str):
            raise ValueError("Invalid or missing 'datetime'")
        if pd.isnull(row["department_id"]) or not isinstance(row["department_id"], (int, float)):
            raise ValueError("Invalid or missing 'department_id'")
        if pd.isnull(row["job_id"]) or not isinstance(row["job_id"], (int, float)):
            raise ValueError("Invalid or missing 'job_id'")

        return {
            "id": int(row["id"]),
            "name": row["name"].strip(),
            "datetime": row["datetime"],
            "department_id": int(row["department_id"]),
            "job_id": int(row["job_id"]),
        }

    def _is_valid_iso_format(self, date_string: str) -> bool:
        """Check if a string is a valid ISO 8601 datetime"""
        try:
            datetime.fromisoformat(date_string.replace("Z", ""))
            return True
        except ValueError:
            return False

    def _validate_department_row(self, row: pd.Series) -> dict:
        if (
            pd.isnull(row["id"]) or not isinstance(row["id"], (int, float)) or row["id"] <= 0
        ):
            raise ValueError("Invalid or missing 'id'")
        if (
            pd.isnull(row["department"])
            or not isinstance(row["department"], str)
            or not row["department"].strip()
        ):
            raise ValueError("Invalid or missing 'department'")

        return {
            "id": int(row["id"]),
            "department": row["department"].strip(),
        }

    def _validate_job_row(self, row: pd.Series) -> dict:
        if (
            pd.isnull(row["id"]) or not isinstance(row["id"], (int, float)) or row["id"] <= 0
        ):
            raise ValueError("Invalid or missing 'id'")
        if (
            pd.isnull(row["job"])
            or not isinstance(row["job"], str)
            or not row["job"].strip()
        ):
            raise ValueError("Invalid or missing 'job'")

        return {
            "id": int(row["id"]),
            "job": row["job"].strip(),
        }