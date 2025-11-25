import redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RedisConnector:
    """Redis database connector"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Redis connector.
        
        Args:
            config: Database configuration dictionary
        
        Raises:
            RedisConnectionError: If connection to Redis fails
        """
        self.config = config
        self.db_id = config.get("id", "unknown")
        
        try:
            self.pool = redis.ConnectionPool(
                host=self.config["host"],
                port=self.config["port"],
                db=self.config["db"],
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            self.client.ping()
            logger.info(f"Redis connection established for '{self.db_id}'")
        except RedisConnectionError as e:
            logger.error(f"Failed to connect to Redis '{self.db_id}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis '{self.db_id}': {e}")
            raise

    def get(self, key: str) -> Optional[str]:
        """
        Get a value from Redis.
        
        Args:
            key: Key to retrieve
        
        Returns:
            Value associated with the key, or None if not found
        
        Raises:
            RedisError: If Redis operation fails
        """
        try:
            value = self.client.get(key)
            if value is not None:
                logger.info(f"Retrieved key '{key}' from '{self.db_id}'")
            else:
                logger.info(f"Key '{key}' not found in '{self.db_id}'")
            return value
            
        except RedisError as e:
            logger.error(f"Redis get operation failed on '{self.db_id}': {e}")
            raise ConnectionError(f"Redis error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get operation on '{self.db_id}': {e}")
            raise

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """
        Set a value in Redis.
        
        Args:
            key: Key to set
            value: Value to store
            ex: Optional expiry time in seconds
        
        Returns:
            True if successful
        
        Raises:
            RedisError: If Redis operation fails
        """
        try:
            result = self.client.set(key, value, ex=ex)
            if result:
                expiry_msg = f" with {ex}s expiry" if ex else ""
                logger.info(f"Set key '{key}' in '{self.db_id}'{expiry_msg}")
            return bool(result)
            
        except RedisError as e:
            logger.error(f"Redis set operation failed on '{self.db_id}': {e}")
            raise ConnectionError(f"Redis error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in set operation on '{self.db_id}': {e}")
            raise

    def delete(self, key: str) -> int:
        """
        Delete a key from Redis.
        
        Args:
            key: Key to delete
        
        Returns:
            Number of keys deleted (0 or 1)
        
        Raises:
            RedisError: If Redis operation fails
        """
        try:
            result = self.client.delete(key)
            if result > 0:
                logger.info(f"Deleted key '{key}' from '{self.db_id}'")
            else:
                logger.info(f"Key '{key}' not found in '{self.db_id}' for deletion")
            return result
            
        except RedisError as e:
            logger.error(f"Redis delete operation failed on '{self.db_id}': {e}")
            raise ConnectionError(f"Redis error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in delete operation on '{self.db_id}': {e}")
            raise

    def close(self):
        """Close Redis connection"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
