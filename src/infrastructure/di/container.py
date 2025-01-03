from dependency_injector import containers, providers
from src.application.services.backup_service import BackupService
from src.infrastructure.persistance.azure_backup_repository import AzureBackupRepository
from src.infrastructure.persistance.azure_sql_repository import (
    AzureSQLEmployeeRepository,
)
from src.infrastructure.azure.storage_service import AzureBlobStorageService
from src.infrastructure.logging.azure_logger import AzureLogger
from src.application.services.ingest_service import IngestService
from src.infrastructure.services.azure_blob_storage_service import (
    AzureBlobStorageServiceInfrastructure,
)
import os

from settings import (
    AZURE_STORAGE_CONNECTION_STRING,
    AZURE_BLOB_CONTAINER_ROW_DATA,
    AZURE_BLOB_CONTAINER_BACKUPS,
    AZURE_SQL_CONNECTION_STRING,
)


class Container(containers.DeclarativeContainer):
    # Load settings
    config = providers.Configuration()
    config.azure_storage_connection_string.override(AZURE_STORAGE_CONNECTION_STRING)
    config.azure_storage_container_name.override(AZURE_BLOB_CONTAINER_ROW_DATA)
    config.azure_storage_container_backup.override(AZURE_BLOB_CONTAINER_BACKUPS)
    config.azure_sql_connection_string.override(AZURE_SQL_CONNECTION_STRING)
    # config.azure_monitor_connection_string.override(AZURE_MONITOR_CONNECTION_STRING)

    # Infrastructure
    logger = providers.Singleton(
        AzureLogger, connection_string=config.azure_monitor_connection_string
    )

    employee_repository = providers.Singleton(
        AzureSQLEmployeeRepository, connection_string=config.azure_sql_connection_string
    )

    storage_service = providers.Singleton(
        AzureBlobStorageServiceInfrastructure,  # Updated class name
        connection_string=config.azure_storage_connection_string,
        container_name=config.azure_storage_container_name,
    )

    # Application Services
    ingest_service = providers.Singleton(
        IngestService,
        employee_repository=employee_repository,
        storage_service=storage_service,
    )
    # Repositorio de respaldos
    backup_repository = providers.Singleton(
        AzureBackupRepository,
        blob_connection_string=config.azure_storage_connection_string,
        container_name=config.azure_storage_container_backup,
    )

    # Servicio de respaldos
    backup_service = providers.Singleton(
        BackupService,
        backup_repository=backup_repository,
        logger=logger,
    )
