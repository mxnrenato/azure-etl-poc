from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.api.routes import employee_routes, backup_routes
from src.infrastructure.api.routes.ingest_routes import router as ingest_router
from src.infrastructure.api.middleware.error_handler import error_handler
import azure.functions as func
from azure.functions import AsgiMiddleware
from src.infrastructure.di.container import Container

app = FastAPI(
    title="ETL API",
    description="API for ETL operations",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.middleware("http")(error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

container = Container()
container.wire(modules=[backup_routes])

app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(backup_routes.router, prefix="/api", tags=["backup"])


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return AsgiMiddleware(app).handle(req, context)
