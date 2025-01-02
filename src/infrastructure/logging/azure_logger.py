from application.interfaces.logger import Logger
from azure.monitor.opentelemetry import AzureMonitorTraceExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import logging
from typing import Any, Dict, Optional
import json


class AzureLogger(Logger):
    def __init__(self, connection_string: str):
        self.exporter = AzureMonitorTraceExporter.from_connection_string(
            connection_string
        )
        provider = TracerProvider()
        processor = BatchSpanProcessor(self.exporter)
        provider.add_span_processor(processor)
        self.tracer = provider.get_tracer(__name__)

    def _format_log(self, message: str, **kwargs: Dict[str, Any]) -> str:
        log_data = {"message": message}
        log_data.update(kwargs)
        return json.dumps(log_data)

    async def info(self, message: str, **kwargs: Dict[str, Any]) -> None:
        with self.tracer.start_as_current_span("info") as span:
            span.set_attribute("log.level", "INFO")
            span.set_attribute("log.message", self._format_log(message, **kwargs))

    async def error(
        self, message: str, error: Optional[Exception] = None, **kwargs: Dict[str, Any]
    ) -> None:
        with self.tracer.start_as_current_span("error") as span:
            span.set_attribute("log.level", "ERROR")
            if error:
                span.set_attribute("error.type", error.__class__.__name__)
                span.set_attribute("error.message", str(error))
            span.set_attribute("log.message", self._format_log(message, **kwargs))

    async def warning(self, message: str, **kwargs: Dict[str, Any]) -> None:
        with self.tracer.start_as_current_span("warning") as span:
            span.set_attribute("log.level", "WARNING")
            span.set_attribute("log.message", self._format_log(message, **kwargs))

    async def debug(self, message: str, **kwargs: Dict[str, Any]) -> None:
        with self.tracer.start_as_current_span("debug") as span:
            span.set_attribute("log.level", "DEBUG")
            span.set_attribute("log.message", self._format_log(message, **kwargs))
