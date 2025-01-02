from datetime import datetime, timezone
from src.application.interfaces.backup_repository import BackupRepository
from src.application.interfaces.logger import Logger
from domain.exceptions.domain_exceptions import BackupError, RestoreError


class BackupService:
    def __init__(self, backup_repository: BackupRepository, logger: Logger):
        self.backup_repository = backup_repository
        self.logger = logger

    async def create_backup(self, table_name: str) -> dict:
        """
        Create a backup for a specific table
        Returns: Dict with backup details
        """
        try:
            await self.logger.info(f"Starting backup for table: {table_name}")

            backup_path = await self.backup_repository.create_backup(table_name)
            if not backup_path:
                raise BackupError(f"Failed to create backup for table: {table_name}")

            await self.logger.info(f"Backup completed successfully: {backup_path}")

            return {
                "status": "success",
                "backup_id": backup_path,
                "table_name": table_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            await self.logger.error(f"Error creating backup: {str(e)}")
            raise BackupError(f"Failed to create backup: {str(e)}")

    async def restore_backup(self, backup_id: str, table_name: str) -> dict:
        """
        Restore a table from a backup
        Returns: Dict with restore operation details
        """
        try:
            await self.logger.info(
                f"Starting restore for table: {table_name} from backup: {backup_id}"
            )

            success = await self.backup_repository.restore_backup(backup_id, table_name)
            if not success:
                raise RestoreError(f"Failed to restore backup for table: {table_name}")

            await self.logger.info("Restore completed successfully")

            return {
                "status": "success",
                "backup_id": backup_id,
                "table_name": table_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            await self.logger.error(f"Error restoring backup: {str(e)}")
            raise RestoreError(f"Failed to restore backup: {str(e)}")

    async def list_backups(self, table_name: str) -> list[dict]:
        """
        List all backups for a specific table
        Returns: List of backup details
        """
        try:
            await self.logger.info(f"Listing backups for table: {table_name}")
            return await self.backup_repository.list_backups(table_name)

        except Exception as e:
            await self.logger.error(f"Error listing backups: {str(e)}")
            raise BackupError(f"Failed to list backups: {str(e)}")
