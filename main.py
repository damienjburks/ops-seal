"""
Module containing examples of common vulnerabilities in web applications.
"""

import os
from fastapi import FastAPI, HTTPException
import redis.asyncio as redis

app = FastAPI()

# Initialize Redis connection
REDIS_HOST = "redis-oss-master.redis.svc.cluster.local"
REDIS_PORT = 6379
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
REDIS = None


@app.on_event("startup")
async def startup_event():
    """
    Connect to Redis on startup with authentication.
    """
    global REDIS
    REDIS = redis.Redis.from_url(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}")
    print("Connected to Redis with authentication")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Disconnect from Redis on shutdown.
    """
    if REDIS:
        await REDIS.close()
        print("Disconnected from Redis")


@app.get("/")
async def root():
    """
    Root endpoint to check if the service is running.
    """
    return {"message": "Welcome to the Redis demo API!"}


@app.post("/")
async def write_to_redis(key: str, value: str):
    """
    Write a key-value pair to Redis.
    """
    try:
        await REDIS.set(key, value)
        return {"message": f"Key '{key}' set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{key}")
async def read_from_redis(key: str):
    """
    Read a value from Redis by key.
    """
    try:
        value = await REDIS.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": value.decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
