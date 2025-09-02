from fastapi import APIRouter
from app.api.v1 import auth, users, roles, branches

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(branches.router)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "NDC UK Backend API is running"}

# API info endpoint
@api_router.get("/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "NDC UK Backend API",
        "version": "1.0.0",
        "description": "Backend API for NDC UK & Ireland Chapter Management System",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "users": "/api/v1/users",
            "roles": "/api/v1/roles", 
            "branches": "/api/v1/branches"
        }
    }