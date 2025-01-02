import datetime
from typing import List
import pyodbc
from src.domain.entities.employee import Employee
from src.domain.repositories.employee_repository import EmployeeRepository
import avro.schema
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, DatumReader


class AzureSQLEmployeeRepository(EmployeeRepository):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        
    async def find_by_department(self, department_id: int) -> List[Employee]:
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM employees WHERE department_id = ?", department_id)
                rows = cursor.fetchall()

                employees = [
                    Employee(
                        id=row.id,
                        name=row.name,
                        hire_datetime=row.hire_datetime,
                        department_id=row.department_id,
                        job_id=row.job_id,
                    )
                    for row in rows
                ]
                return employees
        except Exception as e:
            print(f"Error finding employees by department: {str(e)}")
            return []

    async def find_by_job(self, job_id: int) -> List[Employee]:
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM employees WHERE job_id = ?", job_id)
                rows = cursor.fetchall()

                employees = [
                    Employee(
                        id=row.id,
                        name=row.name,
                        hire_datetime=row.hire_datetime,
                        department_id=row.department_id,
                        job_id=row.job_id,
                    )
                    for row in rows
                ]
                return employees
        except Exception as e:
            print(f"Error finding employees by job: {str(e)}")
            return []

    async def find_by_hire_date_range(
        self, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> List[Employee]:
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM employees WHERE hire_datetime BETWEEN ? AND ?",
                    start_date,
                    end_date,
                )
                rows = cursor.fetchall()

                employees = [
                    Employee(
                        id=row.id,
                        name=row.name,
                        hire_datetime=row.hire_datetime,
                        department_id=row.department_id,
                        job_id=row.job_id,
                    )
                    for row in rows
                ]
                return employees
        except Exception as e:
            print(f"Error finding employees by hire date range: {str(e)}")
            return []
    async def save(self, employee: Employee) -> bool:
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO employees (id, name, hire_datetime, department_id, job_id)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        employee.id,
                        employee.name,
                        employee.hire_datetime,
                        employee.department_id,
                        employee.job_id,
                    ),
                )
                return True
        except Exception as e:
            print(f"Error saving employee: {str(e)}")
            return False

    async def save_batch(self, employees: List[Employee]) -> List[bool]:
        results = []
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            for employee in employees:
                try:
                    cursor.execute(
                        """
                        INSERT INTO employees (id, name, hire_datetime, department_id, job_id)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            employee.id,
                            employee.name,
                            employee.hire_datetime,
                            employee.department_id,
                            employee.job_id,
                        ),
                    )
                    results.append(True)
                except Exception as e:
                    print(f"Error in batch save: {str(e)}")
                    results.append(False)
        return results

    async def backup(self, format: str = "AVRO") -> str:
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM employees")
                rows = cursor.fetchall()

                # Define AVRO schema
                schema = {
                    "name": "Employee",
                    "type": "record",
                    "fields": [
                        {"name": "id", "type": "int"},
                        {"name": "name", "type": "string"},
                        {"name": "hire_datetime", "type": "string"},
                        {"name": "department_id", "type": "int"},
                        {"name": "job_id", "type": "int"},
                    ],
                }

                # Write to AVRO file
                backup_path = (
                    f"backups/employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avro"
                )
                with DataFileWriter(
                    open(backup_path, "wb"),
                    DatumWriter(),
                    avro.schema.parse(str(schema)),
                ) as writer:
                    for row in rows:
                        writer.append(
                            {
                                "id": row.id,
                                "name": row.name,
                                "hire_datetime": row.hire_datetime.isoformat(),
                                "department_id": row.department_id,
                                "job_id": row.job_id,
                            }
                        )

                return backup_path
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            raise

    async def restore(self, backup_path: str) -> bool:
        try:
            # Read AVRO file
            with DataFileReader(open(backup_path, "rb"), DatumReader()) as reader:
                employees = list(reader)

            # Restore to database
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("TRUNCATE TABLE employees")  # Clear existing data

                for emp in employees:
                    cursor.execute(
                        """
                        INSERT INTO employees (id, name, hire_datetime, department_id, job_id)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            emp["id"],
                            emp["name"],
                            emp["hire_datetime"],
                            emp["department_id"],
                            emp["job_id"],
                        ),
                    )

                return True
        except Exception as e:
            print(f"Error restoring backup: {str(e)}")
            return False
