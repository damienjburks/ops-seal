"""
MongoDB API Router
This module defines the API endpoints for interacting with MongoDB.
"""

from fastapi import APIRouter, HTTPException
from clients.mongodb_client import MongoDBClient

mongodb_router = APIRouter(prefix="/api/v1/mongodb", tags=["MongoDB"])

# Initialize the MongoDB client
MONGODB_CLIENT = MongoDBClient()


@mongodb_router.on_event("startup")
async def startup_event():
    """
    Startup event to initialize the MongoDB client connection.
    """
    try:
        await MONGODB_CLIENT.connect()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to connect to MongoDB: {e}"
        )


@mongodb_router.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event to close the MongoDB client connection.
    """
    await MONGODB_CLIENT.close()


@mongodb_router.post("/insert/{collection}")
async def insert_document(collection: str, document: dict):
    """
    Insert a document into a MongoDB collection.
    """
    try:
        result = await MONGODB_CLIENT.db[collection].insert_one(document)
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {e}")


@mongodb_router.get("/find/{collection}")
async def find_documents(collection: str, query: dict):
    """
    Find documents in a MongoDB collection matching a query.
    """
    try:
        cursor = MONGODB_CLIENT.db[collection].find(query)
        docs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            docs.append(doc)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Find failed: {e}")
