# BlobTrigger/__init__.py
import azure.functions as func
import logging
from src.infrastructure.di.container import Container


async def main(myblob: func.InputStream):
    try:
        logging.info(f"Python blob trigger function processed blob: {myblob.name}")

        ingest_service = Container.ingest_service()
        result = await ingest_service.ingest_employees_file(myblob, myblob.name)

        logging.info(f"Processing complete: {result}")

    except Exception as e:
        logging.error(f"Error processing blob {myblob.name}: {str(e)}")
        raise
