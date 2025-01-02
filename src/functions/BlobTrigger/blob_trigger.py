import azure.functions as func
import logging
from application.services.ingest_service import IngestService
from infrastructure.di.container import Container

bp = func.Blueprint()


@bp.blob_trigger(
    arg_name="myblob", path="raw-data/{name}.csv", connection="AzureWebJobsStorage"
)
async def blob_trigger(myblob: func.InputStream):
    """
    Azure Function to process CSV files when they arrive in Blob Storage
    """
    try:
        logging.info(f"Python blob trigger function processed blob: {myblob.name}")

        # Get ingest service from container
        ingest_service = Container.ingest_service()

        # Process the file
        result = await ingest_service.ingest_employees_file(myblob, myblob.name)

        logging.info(f"Processing complete: {result}")

    except Exception as e:
        logging.error(f"Error processing blob {myblob.name}: {str(e)}")
        raise
