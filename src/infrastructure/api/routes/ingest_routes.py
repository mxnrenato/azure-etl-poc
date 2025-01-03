from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from src.application.services.ingest_service import IngestService
from src.infrastructure.di.container import Container

router = APIRouter()

@router.post(
    "/ingest/{table_name}",
    summary="Process and ingest data from file",
    response_model=None
)
async def ingest_data(
    table_name: str,
    file: UploadFile = File(...),
    ingest_service: IngestService = Depends(lambda: Container.ingest_service())
) -> dict:
    try:
        # Process and store the file using the IngestService
        result = await ingest_service.process_and_store_file(file.file, table_name)
        return {"status": "success", "details": result}
    except Exception as e:
        # Log and return an error response
        print(f"Error in ingestion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while ingesting data: {str(e)}"
        )