"""
Redis Client Module
This module provides a Redis client for connecting to a Redis database.
"""

import redis


class RedisClient:
    """
    A client for interacting with a Redis database.

    This class provides methods to connect to and disconnect from a Redis instance.
    It uses asynchronous operations to ensure non-blocking behavior.
    """

    def __init__(self, host, port, password):
        """
        Initializes the RedisClient instance.

        Args:
            host (str): The hostname or IP address of the Redis server.
            port (int): The port number of the Redis server.
            password (str): The password for authenticating with the Redis server.
        """
        self.host = host
        self.port = port
        self.password = password
        self.client = None

    async def connect(self):
        """
        Connects to the Redis server.

        This method initializes the Redis client and attempts to ping the server
        to verify the connection.

        Raises:
            redis.ConnectionError: If the connection to the Redis server fails.
        """
        self.client = redis.Redis.from_url(
            f"redis://:{self.password}@{self.host}:{self.port}"
        )
        try:
            await self.client.ping()
            print("Connected to Redis")
        except redis.ConnectionError:
            print("Failed to connect to Redis")

    async def close(self):
        """
        Closes the connection to the Redis server.

        This method ensures that the Redis client is properly closed to release
        resources.
        """
        if self.client:
            await self.client.close()
            print("Disconnected from Redis")
