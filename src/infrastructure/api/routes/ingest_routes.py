from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from application.services.ingest_service import IngestService
from infrastructure.di.container import Container

router = APIRouter()

@router.post("/employees/upload")
async def upload_employees(
    file: UploadFile = File(...),
    ingest_service: IngestService = Depends(lambda: Container.ingest_service())
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    result = await ingest_service.ingest_employees_file(file.file, file.filename)
    return result