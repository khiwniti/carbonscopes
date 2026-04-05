"""
Health check endpoint for production deployments.
Used by Docker healthchecks and load balancers.
"""
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns 200 OK if the service is healthy.
    Used by:
    - Docker HEALTHCHECK
    - Azure Container Instances health probes
    - Azure App Service health checks
    - Load balancers
    """
    return {
        "status": "healthy",
        "service": "suna-bim-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "BKS cBIM AI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "openapi": "/openapi.json"
    }
