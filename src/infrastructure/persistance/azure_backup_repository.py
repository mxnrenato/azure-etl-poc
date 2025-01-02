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

    def _fetch_table_data(self, table_name: str) -> List[Dict]:
        """
        Fetch all records from the specified SQL table.
        
        Args:
            table_name: Name of the table to fetch
            
        Returns:
            List of dictionaries containing table records
        """
        with pyodbc.connect(self.sql_connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def _format_record(self, record: Dict, table_name: str) -> Dict:
        """
        Format a database record according to the table's AVRO schema.
        
        Args:
            record: Database record to format
            table_name: Name of the table the record belongs to
            
        Returns:
            Formatted record matching AVRO schema
        """
        if table_name == 'employees':
            return {
                'id': record['id'],
                'name': record['name'],
                'datetime': record['datetime'].isoformat() if isinstance(record['datetime'], datetime) else record['datetime'],
                'department_id': record['department_id'],
                'job_id': record['job_id']
            }
        elif table_name == 'departments':
            return {
                'id': record['id'],
                'department': record['department']
            }
        elif table_name == 'jobs':
            return {
                'id': record['id'],
                'job': record['job']
            }
        return record

    async def restore_backup(self, backup_id: str, table_name: str) -> bool:
        """
        Restore a table from an AVRO backup.
        
        Args:
            backup_id: ID of the backup to restore
            table_name: Name of the table to restore to
            
        Returns:
            Boolean indicating success of restore operation
            
        Raises:
            RestoreError: If restore operation fails
        """
        try:
            # Download AVRO file from Azure Blob Storage
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=backup_id
            )
            temp_file_path = f"/tmp/restore_{table_name}.avro"
            
            # Save blob to temporary file
            with open(temp_file_path, "wb") as file:
                blob_data = blob_client.download_blob()
                file.write(blob_data.readall())
            
            # Read records from AVRO file
            with DataFileReader(open(temp_file_path, "rb"), DatumReader()) as reader:
                records = list(reader)
            
            # Restore data to SQL table
            with pyodbc.connect(self.sql_connection_string) as conn:
                cursor = conn.cursor()
                
                # Clear existing table data
                cursor.execute(f"TRUNCATE TABLE {table_name}")
                
                # Insert restored records
                for record in records:
                    fields = ', '.join(record.keys())
                    placeholders = ', '.join(['?' for _ in record])
                    query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
                    cursor.execute(query, list(record.values()))
                
                conn.commit()
                
            return True

        except Exception as e:
            raise RestoreError(f"Failed to restore backup: {str(e)}")

