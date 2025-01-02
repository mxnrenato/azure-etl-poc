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

