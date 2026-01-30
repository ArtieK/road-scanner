from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

# Initialize settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Road Scanner API",
    version="0.1.0",
    description="Transportation comparison API"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns the API status and configuration status for each external service.
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "services": {
            "uber": "configured" if settings.uber_server_token else "not_configured",
            "divvy": "configured",  # Divvy GBFS is public, no auth needed
            "google_maps": "configured" if settings.google_maps_api_key else "not_configured"
        }
    }
