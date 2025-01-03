from datetime import datetime, timezone
from typing import Optional, List, Dict
import avro.schema
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, DatumReader
from azure.storage.blob import BlobServiceClient
import pyodbc
import json
import os
from src.domain.exceptions.domain_exceptions import BackupError, RestoreError
from src.application.interfaces.backup_repository import BackupRepository


class AzureBackupRepository(BackupRepository):
    """
    Repository implementation for handling table backups in AVRO format using Azure Blob Storage.
    Supports backing up and restoring three main tables: employees, departments, and jobs.
    """

    # Define AVRO schemas for each table structure
    SCHEMAS = {
        "employees": {
            "name": "Employee",
            "type": "record",
            "fields": [
                {"name": "id", "type": "int"},
                {"name": "name", "type": "string"},
                {"name": "datetime", "type": "string"},
                {"name": "department_id", "type": "int"},
                {"name": "job_id", "type": "int"},
            ],
        },
        "departments": {
            "name": "Department",
            "type": "record",
            "fields": [
                {"name": "id", "type": "int"},
                {"name": "department", "type": "string"},
            ],
        },
        "jobs": {
            "name": "Job",
            "type": "record",
            "fields": [
                {"name": "id", "type": "int"},
                {"name": "job", "type": "string"},
            ],
        },
    }

    def __init__(self, blob_connection_string: str, container_name: str = "backups"):
        """
        Initialize the backup repository.

        Args:
            blob_connection_string: Azure Blob Storage connection string
            container_name: Name of the container for storing backups
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        self.sql_connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")  # Use the environment variable
        if not self.sql_connection_string:
            raise ValueError("AZURE_SQL_CONNECTION_STRING is not set in environment variables")
        self.container_name = container_name
        self._ensure_container_exists()

    def _ensure_container_exists(self):
        """Ensure the backup container exists in Azure Blob Storage"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            raise BackupError(f"Failed to ensure container exists: {str(e)}")

    async def create_backup(self, table_name: str) -> Optional[str]:
        """
        Create a backup of the specified table in AVRO format.

        Args:
            table_name: Name of the table to backup

        Returns:
            String: Path to the created backup in Azure Blob Storage

        Raises:
            BackupError: If backup creation fails
        """
        try:
            if table_name not in self.SCHEMAS:
                raise BackupError(f"No schema defined for table: {table_name}")

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_name = f"{table_name}/{timestamp}.avro"
            data = self._fetch_table_data(table_name)
            schema = avro.schema.parse(json.dumps(self.SCHEMAS[table_name]))
            temp_file_path = f"/tmp/{backup_name}"

            with DataFileWriter(open(temp_file_path, "wb"), DatumWriter(), schema) as writer:
                for record in data:
                    writer.append(self._format_record(record, table_name))

            with open(temp_file_path, "rb") as data:
                blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=backup_name)
                blob_client.upload_blob(data)

            return backup_name
        except Exception as e:
            raise BackupError(f"Failed to create backup: {str(e)}")

    def _fetch_table_data(self, table_name: str) -> List[Dict]:
        """
        Fetch all records from the specified SQL table.

        Args:
            table_name: Name of the table to fetch

        Returns:
            List of dictionaries containing table records
        """
        try:
            with pyodbc.connect(self.sql_connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name}")
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            raise BackupError(f"Failed to fetch table data: {str(e)}")

    def _format_record(self, record: Dict, table_name: str) -> Dict:
        """
        Format a database record according to the table's AVRO schema.
        """
        try:
            if table_name == "employees":
                return {
                    "id": record["id"],
                    "name": record["name"],
                    "datetime": record["datetime"].isoformat() if isinstance(record["datetime"], datetime) else record["datetime"],
                    "department_id": record["department_id"],
                    "job_id": record["job_id"],
                }
            elif table_name == "departments":
                return {"id": record["id"], "department": record["department"]}
            elif table_name == "jobs":
                return {"id": record["id"], "job": record["job"]}
            return record
        except Exception as e:
            raise BackupError(f"Failed to format record: {str(e)}")

    async def restore_backup(self, backup_id: str, table_name: str) -> bool:
        """
        Restore a table from an AVRO backup.
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=backup_id)
            temp_file_path = f"/tmp/restore_{table_name}.avro"

            with open(temp_file_path, "wb") as file:
                blob_data = blob_client.download_blob()
                file.write(blob_data.readall())

            with DataFileReader(open(temp_file_path, "rb"), DatumReader()) as reader:
                records = list(reader)

            with pyodbc.connect(self.sql_connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(f"TRUNCATE TABLE {table_name}")
                for record in records:
                    fields = ", ".join(record.keys())
                    placeholders = ", ".join(["?" for _ in record])
                    query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
                    cursor.execute(query, list(record.values()))
                conn.commit()
            return True
        except Exception as e:
            raise RestoreError(f"Failed to restore backup: {str(e)}")

    async def list_backups(self, table_name: str) -> List[dict]:
        """
        List all available backups for a specific table.
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            backups = []
            blob_list = container_client.list_blobs(name_starts_with=f"{table_name}/")

            for blob in blob_list:
                backups.append(
                    {
                        "id": blob.name,
                        "table_name": table_name,
                        "created_at": blob.creation_time.isoformat(),
                        "size": blob.size,
                    }
                )

            return backups
        except Exception as e:
            raise BackupError(f"Failed to list backups: {str(e)}")
