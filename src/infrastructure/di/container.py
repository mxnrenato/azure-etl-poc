from dependency_injector import containers, providers
from src.infrastructure.persistance.azure_sql_repository import (
    AzureSQLEmployeeRepository,
)
from src.infrastructure.azure.storage_service import AzureBlobStorageService
from src.infrastructure.logging.azure_logger import AzureLogger
from src.application.services.ingest_service import IngestService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Infrastructure
    logger = providers.Singleton(
        AzureLogger, connection_string=config.azure_monitor_connection_string
    )

    storage_service = providers.Singleton(
        AzureBlobStorageService,
        connection_string=config.azure_storage_connection_string,
    )

    employee_repository = providers.Singleton(
        AzureSQLEmployeeRepository, connection_string=config.azure_sql_connection_string
    )

    # Application Services
    ingest_service = providers.Singleton(
        IngestService,
        employee_repository=employee_repository,
        storage_service=storage_service,
    )
