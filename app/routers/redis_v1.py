"""
REDIS API Router
This module defines the API endpoints for interacting with Redis.
"""

import logging
import redis
from fastapi import APIRouter, HTTPException
from app.clients.redis_client import RedisClient  # Import the RedisClient class

redis_router = APIRouter(prefix="/api/v1/redis", tags=["Redis"])

# Initialize the Redis client
REDIS_CLIENT = RedisClient()


@redis_router.on_event("startup")
async def startup_event():
    """
    Startup event to initialize the Redis client connection.
    """
    try:
        await REDIS_CLIENT.connect()
        logging.info("Redis client connected successfully")
    except redis.ConnectionError:
        logging.error("Failed to connect to Redis")
        raise HTTPException(status_code=500, detail="Failed to connect to Redis")


@redis_router.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event to close the Redis client connection.
    """
    await REDIS_CLIENT.close()


@redis_router.post("/")
async def write_to_redis(key: str, value: str):
    """
    Write a key-value pair to Redis.

    Args:
        key (str): The key to store in Redis.
        value (str): The value to associate with the key.

    Returns:
        dict: A success message.
    """
    try:
        await REDIS_CLIENT.client.set(key, value, ex=3600, keepttl=True)
        return {"message": f"Key '{key}' set successfully with a TTL of 1 hour"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write to Redis: {e}")


@redis_router.get("/{key}")
async def read_from_redis(key: str):
    """
    Read a value from Redis by key.

    Args:
        key (str): The key to retrieve from Redis.

    Returns:
        dict: The key-value pair retrieved from Redis.
    """
    try:
        value = await REDIS_CLIENT.client.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": value.decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read from Redis: {e}")


@redis_router.delete("/{key}")
async def delete_from_redis(key: str):
    """
    Delete a key-value pair from Redis by key.

    Args:
        key (str): The key to delete from Redis.

    Returns:
        dict: A success message.
    """
    try:
        result = await REDIS_CLIENT.client.delete(key)
        if result == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"message": f"Key '{key}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete from Redis: {e}")
