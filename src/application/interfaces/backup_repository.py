from abc import ABC, abstractmethod
from typing import Optional


class BackupRepository(ABC):
    @abstractmethod
    async def create_backup(self, table_name: str) -> Optional[str]:
        """Create a backup for a specific table"""
        pass

    @abstractmethod
    async def restore_backup(self, backup_id: str, table_name: str) -> bool:
        """Restore a table from a backup"""
        pass

    @abstractmethod
    async def list_backups(self, table_name: str) -> list[dict]:
        """List all backups for a specific table"""
        pass
