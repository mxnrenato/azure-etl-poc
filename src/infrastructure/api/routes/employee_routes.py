from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from src.application.services.ingest_service import IngestService
from src.application.dto.employee_dto import BatchIngestDTO
from src.infrastructure.di.container import Container

router = APIRouter()


@router.post("/upload", summary="Upload employee CSV file")
async def upload_employees(
    file: UploadFile = File(...),
    ingest_service: IngestService = Depends(lambda: Container.ingest_service()),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    await ingest_service.store_employees_file(file.file, file.filename)
    return {"message": "File uploaded successfully"}


@router.post("/batch", summary="Ingest batch of employee records")
async def ingest_batch(
    batch: BatchIngestDTO,
    ingest_service: IngestService = Depends(lambda: Container.ingest_service()),
):
    result = await ingest_service.ingest_batch(batch)
    return result
