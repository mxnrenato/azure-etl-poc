from datetime import datetime, timezone
from typing import Optional, List, Dict
import avro.schema
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, DatumReader
from azure.storage.blob import BlobServiceClient
import pyodbc
import json
from domain.exceptions.domain_exceptions import BackupError, RestoreError
from application.interfaces.backup_repository import BackupRepository

class AzureBackupRepository(BackupRepository):
    """
    Repository implementation for handling table backups in AVRO format using Azure Blob Storage.
    Supports backing up and restoring three main tables: employees, departments, and jobs.
    """

    # Define AVRO schemas for each table structure
    SCHEMAS = {
        'employees': {
            'name': 'Employee',
            'type': 'record',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'string'},
                {'name': 'datetime', 'type': 'string'},
                {'name': 'department_id', 'type': 'int'},
                {'name': 'job_id', 'type': 'int'}
            ]
        },
        'departments': {
            'name': 'Department',
            'type': 'record',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'department', 'type': 'string'}
            ]
        },
        'jobs': {
            'name': 'Job',
            'type': 'record',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'job', 'type': 'string'}
            ]
        }
    }

    def __init__(
        self, 
        blob_connection_string: str,
        sql_connection_string: str,
        container_name: str = "backups"
    ):
        """
        Initialize the backup repository.
        
        Args:
            blob_connection_string: Azure Blob Storage connection string
            sql_connection_string: SQL Database connection string
            container_name: Name of the container for storing backups
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        self.sql_connection_string = sql_connection_string
        self.container_name = container_name
        self._ensure_container_exists()

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
            # Validate table schema exists
            if table_name not in self.SCHEMAS:
                raise BackupError(f"No schema defined for table: {table_name}")

            # Generate unique backup name using UTC timestamp
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            backup_name = f"{table_name}/{timestamp}.avro"
            
            # Fetch data from SQL table
            data = self._fetch_table_data(table_name)
            
            # Create temporary AVRO file
            schema = avro.schema.parse(json.dumps(self.SCHEMAS[table_name]))
            temp_file_path = f"/tmp/{backup_name}"
            
            # Write data to AVRO file
            with DataFileWriter(open(temp_file_path, "wb"), DatumWriter(), schema) as writer:
                for record in data:
                    writer.append(self._format_record(record, table_name))
            
            # Upload AVRO file to Azure Blob Storage
            with open(temp_file_path, "rb") as data:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=backup_name
                )
                blob_client.upload_blob(data)

            return backup_name

        except Exception as e:
            raise BackupError(f"Failed to create backup: {str(e)}")
