"""
Module containing examples of common vulnerabilities in web applications.
"""

import os
import json
import mysql.connector
from mysql.connector import Error

from fastapi import FastAPI, HTTPException, Request
import redis.asyncio as redis

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

# Initialize MySQL connection
MYSQL_HOST = "mysql.db.svc.cluster.local"
MYSQL_PORT = 3306
MYSQL = None

# Initialize Redis connection
REDIS_HOST = "redis-oss-master.redis.svc.cluster.local"
REDIS_PORT = 6379
REDIS = None

# File path injected by Vault Agent
VAULT_SECRET_PATH = "/vault/secrets"

# Load Redis password from file
try:
    with open(f"{VAULT_SECRET_PATH}/redis-password", "r", encoding="utf-8") as f:
        REDIS_PASSWORD = f.read().strip()
except FileNotFoundError:
    REDIS_PASSWORD = None
    print("Redis password file not found. Is Vault Agent Injector configured?")

try:
    with open(f"{VAULT_SECRET_PATH}/mysql-creds", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Parse the file into a dictionary
    creds = {}
    for line in lines:
        key, value = line.strip().split("=", 1)
        creds[key] = value

except FileNotFoundError:
    MYSQL_PASSWORD = None
    print("MySQL password file not found. Is Vault Agent Injector configured?")


@app.on_event("startup")
async def startup_event():
    """
    Connect to Redis & MySQL on startup with authentication.
    """
    # Setup Redis connection
    global REDIS
    REDIS = redis.Redis.from_url(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}")

    try:
        await REDIS.ping()
        print("Connected to Redis")
    except redis.ConnectionError:
        print("Failed to connect to Redis")

    # Setup MySQL connection
    global MYSQL
    MYSQL = mysql.connector.connect(
        host=MYSQL_HOST,
        user=creds["username"],
        password=creds["password"],
        database="ops_seal",
        port=MYSQL_PORT,
    )
    if MYSQL.is_connected():
        print("Connected to MySQL")


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
    return {
        "message": "It's ALIVE!",
        "status": "running",
    }


@app.post("/")
async def write_to_redis(request: Request):
    """
    Write a key-value pair to Redis.
    """
    _insert_event(
        service_name="REDIS",
        request_method=request.method,
        endpoint=request.url.path,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        headers=dict(request.headers),
        request_body=await request.json(),
        response_status=200,
        interacted_by=None,  # Replace with actual user if available
    )
    json_body = await request.json()

    try:
        await REDIS.set(
            json_body["key"], json_body["value"], ex=3600, keepttl=True
        )  # Set a TTL of 3600 seconds (1 hour)
        return {"message": f"Key '{key}' set successfully with a TTL of 1 hour"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{key}")
async def read_from_redis(request: Request, key: str):
    """
    Read a value from Redis by key.
    """
    _insert_event(
        service_name="REDIS",
        request_method=request.method,
        endpoint=request.url.path,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        headers=dict(request.headers),
        request_body=None,
        response_status=200,
        interacted_by=None,  # Replace with actual user if available
    )

    try:
        value = await REDIS.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": value.decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{key}")
async def delete_from_redis(request: Request, key: str):
    """
    Delete a key-value pair from Redis by key.
    """
    _insert_event(
        service_name="REDIS",
        request_method=request.method,
        endpoint=request.url.path,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        headers=dict(request.headers),
        request_body=None,
        response_status=200,
        interacted_by=None,  # Replace with actual user if available
    )

    try:
        result = await REDIS.delete(key)
        if result == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"message": f"Key '{key}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _insert_event(
    service_name,
    request_method,
    endpoint,
    ip_address,
    user_agent,
    headers,
    request_body,
    response_status,
    interacted_by,
):
    """
    Inserts an event into the ops_seal_events table.
    """
    try:
        # Prepare the SQL query
        query = """
        INSERT INTO ops_seal_events (
            service_name, request_method, endpoint, ip_address, user_agent,
            headers, request_body, response_status, interacted_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Convert headers and request_body to JSON strings
        headers_json = json.dumps(headers) if headers else None
        request_body_json = json.dumps(request_body) if request_body else None

        # Execute the query
        cursor = MYSQL.cursor()
        cursor.execute(
            query,
            (
                service_name,
                request_method,
                endpoint,
                ip_address,
                user_agent,
                headers_json,
                request_body_json,
                response_status,
                interacted_by,
            ),
        )

        # Commit the transaction
        MYSQL.commit()
        print("Event inserted successfully")
    except Error as e:
        print(f"Error inserting event: {e}")
    finally:
        cursor.close()
