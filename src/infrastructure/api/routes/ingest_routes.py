from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from src.application.services.ingest_service import IngestService
from src.infrastructure.di.container import Container
from io import BytesIO
from typing import Optional

router = APIRouter()

@router.post(
    "/ingest/{table_name}",
    summary="Process and ingest data from file in batches",
    response_model=None,
)
async def ingest_data(
    table_name: str,
    file: UploadFile = File(...),
    batch_size: Optional[int] = Query(default=1000, gt=0, le=5000),
    ingest_service: IngestService = Depends(lambda: Container.ingest_service()),
) -> dict:
    """
    Process and ingest data from CSV file in batches.
    
    Args:
        table_name: Name of the target table (employees, departments, jobs)
        file: CSV file to process
        batch_size: Number of records to process per batch (default: 1000, max: 5000)
        ingest_service: Injected ingest service
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        # Read file content
        contents = await file.read()
        file_obj = BytesIO(contents)
        
        # Process file in batches
        result = await ingest_service.process_and_store_file_in_batches(
            file_obj, 
            table_name,
            batch_size=batch_size
        )
        
        return {
            "status": "success",
            "details": result,
            "message": f"File processed in batches of {batch_size} rows"
        }
        
    except Exception as e:
        # Log and return an error response
        print(f"Error in batch ingestion: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while ingesting data: {str(e)}"
        )