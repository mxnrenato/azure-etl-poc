from datetime import datetime, timezone


from src.application.interfaces.backup_repository import BackupRepository
from src.application.interfaces.logger import Logger
from src.domain.exceptions.domain_exceptions import BackupError, RestoreError


class BackupService:
    def __init__(self, backup_repository: BackupRepository, logger: Logger):
        self.backup_repository = backup_repository
        self.logger = logger

    async def create_backup(self, table_name: str) -> dict:
        """
        Create a backup for a specific table.
        """
        try:
            await self.logger.info(f"Starting backup for table: {table_name}")

            # Delegate to the repository
            backup_path = await self.backup_repository.create_backup(table_name)
            if not backup_path:
                raise BackupError(f"Failed to create backup for table: {table_name}")

            await self.logger.info(f"Backup completed successfully: {backup_path}")

            return {
                "backup_path": backup_path,
                "table_name": table_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            await self.logger.error(f"Error creating backup for {table_name}: {str(e)}")
            raise BackupError(f"Error creating backup: {str(e)}")

    async def restore_backup(self, backup_id: str, table_name: str) -> bool:
        """
        Restore a table from a backup.
        """
        try:
            await self.logger.info(
                f"Starting restore for table: {table_name} from backup: {backup_id}"
            )

            # Delegate to the repository
            success = await self.backup_repository.restore_backup(backup_id, table_name)
            if not success:
                raise RestoreError(f"Failed to restore backup for table: {table_name}")

            await self.logger.info("Restore completed successfully")
            return True

        except Exception as e:
            await self.logger.error(
                f"Error restoring backup for {table_name}: {str(e)}"
            )
            raise RestoreError(f"Error restoring backup: {str(e)}")

    async def list_backups(self, table_name: str) -> list:
        """
        List all backups for a specific table.
        """
        try:
            await self.logger.info(f"Listing backups for table: {table_name}")
            return await self.backup_repository.list_backups(table_name)

        except Exception as e:
            await self.logger.error(f"Error listing backups for {table_name}: {str(e)}")
            raise BackupError(f"Error listing backups: {str(e)}")
