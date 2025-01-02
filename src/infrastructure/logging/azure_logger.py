from typing import Any, Dict, Optional
import json


class AzureLogger:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string  # Retenido por si es necesario más adelante

    def _format_log(self, message: str, **kwargs: Dict[str, Any]) -> str:
        log_data = {"message": message}
        log_data.update(kwargs)
        return json.dumps(log_data)

    async def info(self, message: str, **kwargs: Dict[str, Any]) -> None:
        print(f"INFO: {self._format_log(message, **kwargs)}")

    async def error(
        self, message: str, error: Optional[Exception] = None, **kwargs: Dict[str, Any]
    ) -> None:
        error_details = {
            "error_type": error.__class__.__name__ if error else None,
            "error_message": str(error) if error else None,
        }
        log_message = self._format_log(message, **kwargs, **error_details)
        print(f"ERROR: {log_message}")

    async def warning(self, message: str, **kwargs: Dict[str, Any]) -> None:
        print(f"WARNING: {self._format_log(message, **kwargs)}")

    async def debug(self, message: str, **kwargs: Dict[str, Any]) -> None:
        print(f"DEBUG: {self._format_log(message, **kwargs)}")
