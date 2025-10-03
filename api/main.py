"""FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.routers import (
    pricing,
    addons,
    services,
    features,
    company,
    onboarding,
    leads,
    health,
    onboarding_submission,
    contact_submission,
    submissions,
)

# Create FastAPI application with API Key security scheme for Swagger
app = FastAPI(
    title="Lunaxcode API",
    description="REST API for Lunaxcode website with dual data storage",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    swagger_ui_init_oauth={
        "clientId": "swagger-ui",
        "appName": "Lunaxcode API",
    },
)

# Add API Key security scheme to OpenAPI schema
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Enter your API key (from .env file)"
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    if not settings.is_production:
        # In development, show detailed error
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__}
        )
    else:
        # In production, hide internal errors
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


# Include routers with /api/v1 prefix
API_V1_PREFIX = "/api/v1"

app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(pricing.router, prefix=API_V1_PREFIX)
app.include_router(addons.router, prefix=API_V1_PREFIX)
app.include_router(services.router, prefix=API_V1_PREFIX)
app.include_router(features.router, prefix=API_V1_PREFIX)
app.include_router(company.router, prefix=API_V1_PREFIX)
app.include_router(onboarding.router, prefix=API_V1_PREFIX)
app.include_router(leads.router, prefix=API_V1_PREFIX)
app.include_router(onboarding_submission.router, prefix=API_V1_PREFIX)
app.include_router(contact_submission.router, prefix=API_V1_PREFIX)
app.include_router(submissions.router, prefix=API_V1_PREFIX)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Lunaxcode API",
        "version": "0.1.0",
        "docs": "/api/v1/docs"
    }


@app.get("/favicon.ico")
@app.get("/favicon.png")
async def favicon():
    """Return 204 No Content for favicon requests to prevent errors"""
    from fastapi import Response
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)