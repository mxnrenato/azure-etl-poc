from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.api.routes import employee_routes, backup_routes
from src.infrastructure.api.middleware.error_handler import error_handler
import azure.functions as func
from azure.functions import AsgiMiddleware

app = FastAPI(
    title="ETL API",
    description="API for ETL operations",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.middleware("http")(error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    employee_routes.router,
    prefix="/api",
    tags=["employees"]
)

app.include_router(
    backup_routes.router,
    prefix="/api",
    tags=["system"]
)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return AsgiMiddleware(app).handle(req, context)