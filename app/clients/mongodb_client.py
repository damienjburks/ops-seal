"""
MongoDB Client Module
This module provides an async MongoDB client for connecting to a MongoDB database.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from utils.secrets import VaultSecretsLoader


class MongoDBClient:
    """
    A client for interacting with a MongoDB database asynchronously.

    This class provides methods to connect to and disconnect from a MongoDB instance.
    """

    def __init__(self, uri="mongodb-svc.mongodb.svc.cluster.local", db_name="damien"):
        """
        Initializes the MongoDBClient instance.

        Args:
            uri (str): The MongoDB connection URI. If None, loads from Vault.
            db_name (str): The name of the database to use.
        """
        if uri is None:
            uri = VaultSecretsLoader().load_secret("mongodb-uri")
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    async def connect(self):
        """
        Connects to the MongoDB server and initializes the database client.
        """
        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.db_name]
            # Test connection
            await self.db.command("ping")
            logging.info("Connected to MongoDB")
        except Exception as e:
            logging.error("Failed to connect to MongoDB: %s", e)
            raise

    async def close(self):
        """
        Closes the connection to the MongoDB server.
        """
        if self.client:
            self.client.close()
            logging.info("MongoDB client closed")
