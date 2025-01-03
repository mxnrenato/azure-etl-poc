from fastapi import APIRouter, Depends, HTTPException
from src.application.services.backup_service import BackupService
from src.infrastructure.di.container import Container

router = APIRouter()


@router.post("/backup/{table_name}", summary="Create backup for a specific table")
async def create_backup(
    table_name: str,
    backup_service: BackupService = Depends(lambda: Container.backup_service()),
):
    try:
        result = await backup_service.create_backup(table_name)
        return {"status": "success", "backup_details": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create backup: {str(e)}"
        )


@router.post("/restore/{table_name}/{backup_id}", summary="Restore a table from backup")
async def restore_backup(
    table_name: str,
    backup_id: str,
    backup_service: BackupService = Depends(lambda: Container.backup_service()),
):
    try:
        success = await backup_service.restore_backup(backup_id, table_name)
        return {"status": "success" if success else "failed"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to restore backup: {str(e)}"
        )


@router.get("/backups/{table_name}", summary="List backups for a specific table")
async def list_backups(
    table_name: str,
    backup_service: BackupService = Depends(lambda: Container.backup_service()),
):
    try:
        backups = await backup_service.list_backups(table_name)
        return {"status": "success", "backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")
