from fastapi import Request
from fastapi.responses import JSONResponse
from domain.exceptions.domain_exceptions import DomainException, ValidationError

async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={"error": "Validation error", "detail": str(e)}
        )
    except DomainException as e:
        return JSONResponse(
            status_code=400,
            content={"error": "Domain error", "detail": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )