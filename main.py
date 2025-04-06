"""
Module containing examples of common vulnerabilities in web applications.
"""

from fastapi import FastAPI, HTTPException
import aioredis

app = FastAPI()

# Initialize Redis connection
redis_host = "redis-oss-master.redis.svc.cluster.local"
redis_port = 6379


@app.on_event("startup")
async def startup_event():
    """
    Connect to Redis on startup.
    """
    global redis
    redis = await aioredis.from_url(f"redis://{redis_host}:{redis_port}")
    print("Connected to Redis")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Disconnect from Redis on shutdown.
    """
    await redis.close()
    print("Disconnected from Redis")


@app.post("/")
async def write_to_redis(key: str, value: str):
    """
    Write a key-value pair to Redis.
    """
    try:
        await redis.set(key, value)
        return {"message": f"Key '{key}' set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def read_from_redis(key: str):
    """
    Read a value from Redis by key.
    """
    try:
        value = await redis.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": value.decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
