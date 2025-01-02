from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.api.routes import employee_routes, backup_routes
from src.infrastructure.api.middleware.error_handler import error_handler

import azure.functions as func
from azure.functions import AsgiMiddleware

# Define la aplicación FastAPI
app = FastAPI(
    title="ETL API",
    description="API for ETL operations",
    version="1.0.0"
)

# Configura el middleware
app.middleware("http")(error_handler)  # Manejo de errores global
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción para restringir orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura las rutas
app.include_router(employee_routes.router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(backup_routes.router, prefix="/api/v1/system", tags=["system"])

# Conecta FastAPI con Azure Functions
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return AsgiMiddleware(app).handle(req, context)
