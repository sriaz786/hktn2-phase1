"""FastAPI application initialization."""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import create_db_tables, init_logging, settings
from app.database import get_db_session
from app.models.schemas import ErrorCode, ErrorResponse

# Initialize logging
init_logging()
logger = logging.getLogger(__name__)


# Global service instances (will be initialized in lifespan)
mcp_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Startup
    logger.info("Starting up application...")
    logger.info("Database URL: %s", settings.database_url[:20] + "...")
    logger.info("OpenAI Model: %s", settings.openai_model)

    # Create database tables
    try:
        create_db_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables: %s", e)
        raise

    # Initialize services
    global mcp_service

    from app.services.mcp_service import MCPService
    from app.services.todo_service import TodoService

    # Services will be created per-request in route handlers
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="Evolution of Todo API",
    version="1.0.0",
    description="Todo management system with AI assistance and MCP integration",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to each request for tracing.

    Args:
        request: HTTP request
        call_next: Next middleware or route handler

    Returns:
        HTTP response
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors.

    Args:
        request: HTTP request
        exc: Validation exception

    Returns:
        JSON error response
    """
    logger.warning("Validation error on %s: %s", request.url, exc.errors())

    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors[field] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error={
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Invalid request data",
                "details": errors,
            }
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions.

    Args:
        request: HTTP request
        exc: HTTP exception

    Returns:
        JSON error response
    """
    logger.warning("HTTP exception on %s: %s", request.url, exc.detail)

    error_code = ErrorCode.NOT_FOUND if exc.status_code == 404 else ErrorCode.INTERNAL_ERROR

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error={
                "code": error_code,
                "message": exc.detail,
            }
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions.

    Args:
        request: HTTP request
        exc: Exception

    Returns:
        JSON error response
    """
    logger.exception("Unhandled exception on %s: %s", request.url, exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error={
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "An unexpected error occurred",
            }
        ).model_dump(),
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring.

    Returns:
        Health status
    """
    return {"status": "healthy", "message": "API is operational"}


# Include routers
from app.api.v1 import ai, todos

app.include_router(todos.router, prefix="/api/v1", tags=["Todos"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information.

    Returns:
        API information
    """
    return {
        "name": "Evolution of Todo API",
        "version": "1.0.0",
        "status": "Phase 1",
        "docs": "/docs",
    }


# Log startup
logger.info("FastAPI application initialized")
