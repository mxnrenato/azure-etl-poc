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
