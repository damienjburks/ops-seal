"""
Main module for the Ops-Seal API.
This module initializes the FastAPI application, sets up logging,
and includes various routers for handling different API endpoints.
It serves as the entry point for the application.
"""

import logging
import uvicorn
from fastapi import FastAPI
from utils.cron import DefaultScheduler
from routers.redis_v1 import redis_router
from routers.tfc_v1 import tfc_router
from routers.mongodb_v1 import mongodb_router


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


@app.get("/")
async def root():
    """
    Root endpoint to check if the service is running.
    """
    return {"message": "It's ALIVE!", "status": "running"}


# Include routers
app.include_router(redis_router)
app.include_router(tfc_router)
app.include_router(mongodb_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        use_colors=True,
    )
