from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
from application.services.ingest_service import IngestService
from application.dto.employee_dto import EmployeeDTO, BatchIngestDTO
from infrastructure.di.container import Container

router = APIRouter()


@router.post("/upload", summary="Upload employee CSV file")
async def upload_employees(
    file: UploadFile = File(...),
    ingest_service: IngestService = Depends(lambda: Container.ingest_service()),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    result = await ingest_service.ingest_employees_file(file.file, file.filename)
    return result


@router.post("/batch", summary="Ingest batch of employee records")
async def ingest_batch(
    batch: BatchIngestDTO,
    ingest_service: IngestService = Depends(lambda: Container.ingest_service()),
):
    result = await ingest_service.ingest_batch(batch)
    return result


# src/infrastructure/api/routes/backup_routes.py
from fastapi import APIRouter, Depends, HTTPException
from application.services.backup_service import BackupService
from infrastructure.di.container import Container

router = APIRouter()


@router.post("/backup", summary="Create backup of employees table")
async def create_backup(
    backup_service: BackupService = Depends(lambda: Container.backup_service()),
):
    try:
        backup_path = await backup_service.create_backup()
        return {"backup_path": backup_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore/{backup_id}", summary="Restore from backup")
async def restore_backup(
    backup_id: str,
    backup_service: BackupService = Depends(lambda: Container.backup_service()),
):
    try:
        success = await backup_service.restore_backup(backup_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
