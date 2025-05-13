"""
TFC API v1 Router
This module defines the API endpoints for interacting with the TFC client.
"""

from fastapi import APIRouter, HTTPException

from clients.tfc_client import TfcClient

tfc_router = APIRouter(prefix="/api/v1/tfc", tags=["Redis"])


@tfc_router.post("/start-processing-job")
async def start_processing_job():
    """
    Start a processing job for the TFC client.
    """
    try:
        TfcClient().run()
        return {"message": "Processing job started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
