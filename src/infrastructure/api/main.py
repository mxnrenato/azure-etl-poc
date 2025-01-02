from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import employee_routes, backup_routes
from .middleware.error_handler import error_handler


def create_app() -> FastAPI:
    app = FastAPI(
        title="ETL API", description="API for ETL operations", version="1.0.0"
    )

    # Middleware
    app.middleware("http")(error_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(
        employee_routes.router, prefix="/api/v1/employees", tags=["employees"]
    )
    app.include_router(backup_routes.router, prefix="/api/v1/system", tags=["system"])

    return app
