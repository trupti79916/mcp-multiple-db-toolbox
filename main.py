from mcp.server.fastmcp import FastMCP
from config_parser import load_config
# REMOVED: Top-level connector imports to prevent crash-on-startup
from typing import Dict, Any, Optional
import logging
import sys
import os
from dotenv import load_dotenv

# 1. Setup paths safely
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

# 2. Configure logging FIRST (Force stderr)
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# 3. Load Environment
load_dotenv(env_path)
logger.info(f"Environment loaded from: {env_path}")

# Initialize FastMCP server
mcp = FastMCP("multi-db-toolbox")

# Global connector storage
connectors: Dict[str, Any] = {}
db_configs_cache = []

def load_db_configs():
    """Load database configurations without initializing connectors"""
    global db_configs_cache
    if not db_configs_cache:
        # Pass current_dir to ensure it finds config.yaml correctly
        config_path = os.path.join(current_dir, "config.yaml")
        db_configs_cache = load_config(config_path)
        logger.info(f"Loaded {len(db_configs_cache)} database configuration(s)")
    return db_configs_cache

def get_or_create_connector(db_id: str):
    """Get existing connector or create new one on demand"""
    if db_id in connectors:
        return connectors[db_id]
    
    configs = load_db_configs()
    config = next((c for c in configs if c["id"] == db_id), None)
    
    if not config:
        raise ValueError(f"Database '{db_id}' not found in configuration")
    
    db_type = config["type"]
    
    # LAZY IMPORTS: Import only when needed to prevent startup crashes
    try:
        if db_type == "postgres":
            from connectors.postgres import PostgresConnector
            connectors[db_id] = PostgresConnector(config)
        elif db_type == "mongodb":
            from connectors.mongodb import MongoDBConnector
            connectors[db_id] = MongoDBConnector(config)
        elif db_type == "redis":
            from connectors.redis import RedisConnector
            connectors[db_id] = RedisConnector(config)
        else:
            raise ValueError(f"Unknown database type: {db_type}")
            
        logger.info(f"Initialized {db_type} connector: {db_id}")
        return connectors[db_id]
    except ImportError as e:
        # This will now show up in the chat instead of crashing the connection
        error_msg = f"Missing dependency for {db_type}. Error: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        logger.error(f"Failed to initialize {db_type} connector '{db_id}': {e}")
        raise

# PostgreSQL Tools
@mcp.tool()
def query_postgres(db_id: str, query: str, params: Optional[str] = None) -> list:
    """Execute a SQL query against a PostgreSQL database."""
    # We don't import PostgresConnector here to avoid circular/type errors at top level
    # Just check class name string or trust the connector
    connector = get_or_create_connector(db_id)
    
    import json
    parsed_params = json.loads(params) if params else None
    return connector.execute_query(query, tuple(parsed_params) if parsed_params else None)

# MongoDB Tools
@mcp.tool()
def find_mongodb(db_id: str, collection: str, query: str, projection: Optional[str] = None) -> list:
    """Find documents in a MongoDB collection."""
    connector = get_or_create_connector(db_id)
    
    import json
    query_dict = json.loads(query)
    projection_dict = json.loads(projection) if projection else None
    return connector.find(collection, query_dict, projection_dict)

@mcp.tool()
def insert_mongodb(db_id: str, collection: str, document: str) -> str:
    """Insert a document into a MongoDB collection."""
    connector = get_or_create_connector(db_id)
    
    import json
    doc_dict = json.loads(document)
    return connector.insert_one(collection, doc_dict)

@mcp.tool()
def list_collections_mongodb(db_id: str) -> list:
    """
    List all collections in a MongoDB database.
    """
    connector = get_or_create_connector(db_id) 
    return connector.list_collections()

# Redis Tools
@mcp.tool()
def get_redis(db_id: str, key: str) -> Optional[str]:
    """Get a value from Redis cache."""
    connector = get_or_create_connector(db_id)
    return connector.get(key)

@mcp.tool()
def set_redis(db_id: str, key: str, value: str, expiry: Optional[int] = None) -> bool:
    """Set a value in Redis cache."""
    connector = get_or_create_connector(db_id)
    return connector.set(key, value, ex=expiry)

@mcp.tool()
def delete_redis(db_id: str, key: str) -> int:
    """Delete a key from Redis cache."""
    connector = get_or_create_connector(db_id)
    return connector.delete(key)

if __name__ == "__main__":
    logger.info("Starting Multi-DB MCP Server...")
    # Run using the python executable logic we discussed earlier
    mcp.run(transport="stdio")
