from hdbcli import dbapi
from typing import Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)

class HANAConnector:
    """SAP HANA database connector"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize HANA connector.
        
        Args:
            config: Database configuration dictionary
        
        Raises:
            Exception: If connection to database fails
        """
        self.config = config
        self.db_id = config.get("id", "unknown")
        self.connection = None
        
        try:
            self.connection = dbapi.connect(
                address=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                # Optional: database name if specified
                databaseName=self.config.get("dbname", "")
            )
            logger.info(f"HANA connection established for '{self.db_id}'")
        except Exception as e:
            logger.error(f"Failed to connect to HANA database '{self.db_id}': {e}")
            raise

    def get_connection(self):
        """Get the database connection"""
        if not self.connection or not self.connection.isconnected():
            try:
                self.connection = dbapi.connect(
                    address=self.config["host"],
                    port=self.config["port"],
                    user=self.config["user"],
                    password=self.config["password"],
                    databaseName=self.config.get("dbname", "")
                )
                logger.info(f"HANA connection re-established for '{self.db_id}'")
            except Exception as e:
                logger.error(f"Failed to reconnect to HANA database '{self.db_id}': {e}")
                raise
        return self.connection

    def execute_query(self, query: str, params: tuple = None) -> Union[List[Dict[str, Any]], str]:
        """
        Execute a SQL query against the HANA database.
        
        Args:
            query: SQL query to execute
            params: Optional tuple of query parameters
        
        Returns:
            For SELECT queries: List of dictionaries containing results
            For other queries: String indicating number of rows affected
        
        Raises:
            Exception: If SQL query fails or database connection fails
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if query returns results
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                logger.info(f"Query executed successfully on '{self.db_id}', returned {len(results)} row(s)")
                return results
            else:
                # For INSERT, UPDATE, DELETE, etc.
                conn.commit()
                affected = cursor.rowcount
                logger.info(f"Query executed successfully on '{self.db_id}', affected {affected} row(s)")
                return f"{affected} row(s) affected"
                    
        except Exception as e:
            logger.error(f"Error executing query on '{self.db_id}': {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def list_schemas(self) -> List[Dict[str, Any]]:
        """
        List all schemas in the HANA database.
        
        Returns:
            List of dictionaries containing schema information
        
        Raises:
            Exception: If query fails
        """
        query = """
        SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME
        FROM SYS.SCHEMAS
        ORDER BY SCHEMA_NAME
        """
        try:
            results = self.execute_query(query)
            logger.info(f"Retrieved {len(results)} schema(s) from '{self.db_id}'")
            return results
        except Exception as e:
            logger.error(f"Failed to list schemas on '{self.db_id}': {e}")
            raise

    def list_tables(self, schema_name: str = None) -> List[Dict[str, Any]]:
        """
        List all tables in the HANA database or in a specific schema.
        
        Args:
            schema_name: Optional schema name to filter tables
        
        Returns:
            List of dictionaries containing table information
        
        Raises:
            Exception: If query fails
        """
        if schema_name:
            query = """
            SELECT SCHEMA_NAME, TABLE_NAME, TABLE_TYPE, RECORD_COUNT
            FROM SYS.M_TABLES
            WHERE SCHEMA_NAME = ?
            ORDER BY TABLE_NAME
            """
            params = (schema_name,)
        else:
            query = """
            SELECT SCHEMA_NAME, TABLE_NAME, TABLE_TYPE, RECORD_COUNT
            FROM SYS.M_TABLES
            ORDER BY SCHEMA_NAME, TABLE_NAME
            """
            params = None
        
        try:
            results = self.execute_query(query, params)
            logger.info(f"Retrieved {len(results)} table(s) from '{self.db_id}'" + 
                       (f" in schema '{schema_name}'" if schema_name else ""))
            return results
        except Exception as e:
            logger.error(f"Failed to list tables on '{self.db_id}': {e}")
            raise

    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info(f"Closed HANA connection for '{self.db_id}'")
            except Exception as e:
                logger.error(f"Error closing HANA connection for '{self.db_id}': {e}")
