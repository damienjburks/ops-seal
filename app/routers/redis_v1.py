"""
REDIS API Router
This module defines the API endpoints for interacting with Redis.
"""

from fastapi import APIRouter, Request, HTTPException

redis_router = APIRouter(prefix="/api/v1/redis", tags=["Redis"])


@redis_router.post("/")
async def write_to_redis(request: Request):
    """
    Write a key-value pair to Redis.
    """
    json_body = await request.json()
    key = json_body.get("key")
    value = json_body.get("value")

    try:
        await REDIS_CLIENT.client.set(key, value, ex=3600, keepttl=True)
        return {"message": f"Key '{key}' set successfully with a TTL of 1 hour"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@redis_router.get("/{key}")
async def read_from_redis(request: Request, key: str):
    """
    Read a value from Redis by key.
    """
    try:
        value = await REDIS_CLIENT.client.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": value.decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@redis_router.delete("/{key}")
async def delete_from_redis(request: Request, key: str):
    """
    Delete a key-value pair from Redis by key.
    """
    try:
        result = await REDIS_CLIENT.client.delete(key)
        if result == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"message": f"Key '{key}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
