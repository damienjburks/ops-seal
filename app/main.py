"""
Main module for the Ops-Seal API.
This module initializes the FastAPI application, sets up logging,
and includes various routers for handling different API endpoints.
It serves as the entry point for the application.
"""

import logging
import uvicorn
from fastapi import FastAPI, APIRouter
from utils.cron import DefaultScheduler
from routers.redis_v1 import redis_router
from routers.tfc_v1 import tfc_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize FastAPI app
app = FastAPI(
    title="Ops-Seal",
    description="An API demonstrating interactions with Redis and MySQL, including event logging.",
    version="1.0.0",
    contact={
        "name": "Damien Burks",
        "email": "damien@devsecblueprint.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Start Scheduler
scheduler = DefaultScheduler(interval_hours=24)
scheduler.start()

# Routers
root_router = APIRouter()

# Include routers
app.include_router(root_router)
app.include_router(redis_router)
app.include_router(tfc_router)


@root_router.get("/")
async def root():
    """
    Root endpoint to check if the service is running.
    """
    return {"message": "It's ALIVE!", "status": "running"}

if __name__ == "__main__":
    uvicorn.run(app,
        host="0.0.0.0",
        port=8080, 
        log_level="info",
        reload=True,
        use_colors=True,
    )