from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.exceptions import NDCException
from app.core.database import supabase_client
from app.api.v1.router import api_router
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Backend API for NDC UK & Ireland Chapter Management System",
    debug=settings.DEBUG
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path} - {request.client.host}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Exception handlers
@app.exception_handler(NDCException)
async def ndc_exception_handler(request: Request, exc: NDCException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "description": "Backend API for NDC UK & Ireland Chapter Management System",
        "documentation": "/docs",
        "api_base": "/api/v1",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/minute")
async def health_check(request: Request):
    """Comprehensive health check"""
    try:
        # Check database connection
        db_healthy = await supabase_client.health_check()
        
        health_status = {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": time.time(),
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "connected" if db_healthy else "disconnected"
        }
        
        if not db_healthy:
            return JSONResponse(status_code=503, content=health_status)
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e) if settings.DEBUG else "Service unavailable"
            }
        )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Test database connection
    try:
        db_healthy = await supabase_client.health_check()
        if db_healthy:
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed")
    except Exception as e:
        logger.error(f"Database connection error: {e}")

# Shutdown event
@app.on_event("shutdown") 
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

# Add OpenAPI documentation customization
app.openapi_tags = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization endpoints",
    },
    {
        "name": "User Management", 
        "description": "User profile and membership management endpoints",
    },
    {
        "name": "Role Management",
        "description": "Role assignment and executive position management endpoints",
    },
    {
        "name": "Branch Management",
        "description": "Branch and membership management endpoints",
    }
]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )