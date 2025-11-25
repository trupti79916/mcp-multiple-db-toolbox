import os
import yaml
from typing import List, Dict, Any
import logging
import sys

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Configuration error exception"""
    pass

def load_config(path: str = None) -> List[Dict[str, Any]]:
    """
    Load database configuration from YAML file and resolve environment variables.
    
    Args:
        path: Path to configuration file. If None, looks for config.yaml in this file's directory.
    """
    # FIX: Auto-detect the absolute path if no path is provided
    if path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "config.yaml")

    try:
        # Check if file exists explicitly to give better error messages
        if not os.path.exists(path):
            # Try looking one level up just in case
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            parent_path = os.path.join(parent_dir, "config.yaml")
            if os.path.exists(parent_path):
                path = parent_path
            else:
                logger.error(f"Config file not found at: {path}")
                raise ConfigError(f"Configuration file not found: {path}")

        with open(path, "r") as f:
            config = yaml.safe_load(f)
            
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        raise ConfigError(f"Error reading config file: {e}")
    
    databases = config.get("databases", [])
    
    if not databases:
        logger.warning(f"No databases found in {path}")
        # Return empty list instead of crashing, unless you want strict enforcement
        # raise ConfigError("No databases configured in config.yaml")
        return []
    
    missing_vars = []
    
    for db_config in databases:
        db_id = db_config.get("id", "unknown")
        
        # Resolve environment variables
        for key, value in db_config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                resolved_value = os.environ.get(env_var)
                
                if resolved_value is None:
                    missing_vars.append(f"{env_var} (required by {db_id}.{key})")
                    logger.error(f"Missing environment variable: {env_var} for {db_id}.{key}")
                else:
                    db_config[key] = resolved_value
    
    if missing_vars:
        raise ConfigError(
            f"Missing required environment variables:\n" + 
            "\n".join(f"  - {var}" for var in missing_vars)
        )
    
    # Validate database configurations
    for db_config in databases:
        validate_db_config(db_config)
    
    return databases

def validate_db_config(config: Dict[str, Any]) -> None:
    """Validate a database configuration."""
    if "id" not in config:
        raise ConfigError("Database configuration missing 'id' field")
    
    if "type" not in config:
        raise ConfigError(f"Database '{config['id']}' missing 'type' field")
    
    db_type = config["type"]
    db_id = config["id"]
    
    if db_type == "postgres":
        required_fields = ["host", "port", "user", "password", "dbname"]
        for field in required_fields:
            if field not in config or config[field] is None:
                raise ConfigError(f"PostgreSQL database '{db_id}' missing field: {field}")
    
    elif db_type == "mongodb":
        if "uri" not in config or config["uri"] is None:
            raise ConfigError(f"MongoDB database '{db_id}' missing field: uri")
        if "database" not in config or config["database"] is None:
            raise ConfigError(f"MongoDB database '{db_id}' missing field: database")
    
    elif db_type == "redis":
        required_fields = ["host", "port", "db"]
        for field in required_fields:
            if field not in config or config[field] is None:
                raise ConfigError(f"Redis database '{db_id}' missing field: {field}")
    
    else:
        raise ConfigError(f"Unknown database type '{db_type}'")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    try:
        db_configs = load_config()
        print("Config loaded successfully")
    except ConfigError as e:
        print(f"Error: {e}")