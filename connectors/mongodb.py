from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MongoDBConnector:
    """MongoDB database connector"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MongoDB connector.
        
        Args:
            config: Database configuration dictionary
        
        Raises:
            ConnectionFailure: If connection to MongoDB fails
        """
        self.config = config
        self.db_id = config.get("id", "unknown")
        
        try:
            # For MongoDB Atlas, we need to handle SSL certificates properly
            self.client = MongoClient(
                self.config["uri"],
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                tlsAllowInvalidCertificates=True,  # Allow self-signed certificates for development
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.config["database"]]
            logger.info(f"MongoDB connection established for '{self.db_id}'")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB '{self.db_id}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB '{self.db_id}': {e}")
            raise

    def find(self, collection_name: str, query: Dict[str, Any], projection: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find documents in a MongoDB collection.
        
        Args:
            collection_name: Name of the collection
            query: Query filter dictionary
            projection: Optional projection dictionary
        
        Returns:
            List of matching documents
        
        Raises:
            OperationFailure: If MongoDB operation fails
        """
        try:
            collection = self.db[collection_name]
            results = []
            
            cursor = collection.find(query, projection)
            for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                results.append(doc)
            
            logger.info(f"Found {len(results)} document(s) in '{self.db_id}.{collection_name}'")
            return results
            
        except OperationFailure as e:
            logger.error(f"MongoDB operation failed on '{self.db_id}.{collection_name}': {e}")
            raise ValueError(f"MongoDB operation error: {e}")
        except PyMongoError as e:
            logger.error(f"PyMongo error on '{self.db_id}.{collection_name}': {e}")
            raise ConnectionError(f"MongoDB error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in find operation on '{self.db_id}.{collection_name}': {e}")
            raise

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        Insert a document into a MongoDB collection.
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
        
        Returns:
            Inserted document ID as string
        
        Raises:
            OperationFailure: If MongoDB operation fails
        """
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            inserted_id = str(result.inserted_id)
            
            logger.info(f"Inserted document with ID {inserted_id} into '{self.db_id}.{collection_name}'")
            return inserted_id
            
        except OperationFailure as e:
            logger.error(f"MongoDB insert failed on '{self.db_id}.{collection_name}': {e}")
            raise ValueError(f"MongoDB insert error: {e}")
        except PyMongoError as e:
            logger.error(f"PyMongo error on '{self.db_id}.{collection_name}': {e}")
            raise ConnectionError(f"MongoDB error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in insert operation on '{self.db_id}.{collection_name}': {e}")
            raise
    def list_collections(self) -> List[str]:
        """
        List all collection names in the current database.
        
        Returns:
            List of collection names
        """
        try:
            collections = self.db.list_collection_names()
            logger.info(f"Listed {len(collections)} collections in '{self.db_id}'")
            return collections
        except Exception as e:
            logger.error(f"Failed to list collections in '{self.db_id}': {e}")
            raise

    def close(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
