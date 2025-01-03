from fastapi import APIRouter, Depends, HTTPException
from src.application.services.backup_service import BackupService
from src.infrastructure.di.container import Container
from dependency_injector.wiring import Provide, inject

router = APIRouter()


@router.post("/backup/{table_name}")
@inject
async def create_backup(
    table_name: str,
    backup_service: BackupService = Depends(Provide[Container.backup_service]),
):
    try:
        result = await backup_service.create_backup(table_name)
        return {"status": "success", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore/{table_name}")
@inject
async def restore_backup(
    table_name: str,
    backup_id: str,
    backup_service: BackupService = Depends(Provide[Container.backup_service]),
):
    try:
        success = await backup_service.restore_backup(backup_id, table_name)
        return {"status": "success" if success else "failure"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
