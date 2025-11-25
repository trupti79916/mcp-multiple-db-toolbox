import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import OperationalError, ProgrammingError
from typing import Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)

class PostgresConnector:
    """PostgreSQL database connector with connection pooling"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PostgreSQL connector with connection pool.
        
        Args:
            config: Database configuration dictionary
        
        Raises:
            OperationalError: If connection to database fails
        """
        self.config = config
        self.db_id = config.get("id", "unknown")
        
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                user=self.config["user"],
                password=self.config["password"],
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["dbname"],
            )
            logger.info(f"PostgreSQL connection pool created for '{self.db_id}'")
        except OperationalError as e:
            logger.error(f"Failed to create PostgreSQL connection pool for '{self.db_id}': {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.pool.getconn()
        except Exception as e:
            logger.error(f"Failed to get connection from pool for '{self.db_id}': {e}")
            raise

    def release_connection(self, conn):
        """Return a connection to the pool"""
        try:
            self.pool.putconn(conn)
        except Exception as e:
            logger.error(f"Failed to release connection to pool for '{self.db_id}': {e}")

    def execute_query(self, query: str, params: tuple = None) -> Union[List[Dict[str, Any]], str]:
        """
        Execute a SQL query against the PostgreSQL database.
        
        Args:
            query: SQL query to execute
            params: Optional tuple of query parameters
        
        Returns:
            For SELECT queries: List of dictionaries containing results
            For other queries: String indicating number of rows affected
        
        Raises:
            ProgrammingError: If SQL query is malformed
            OperationalError: If database connection fails
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
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
                    
        except ProgrammingError as e:
            logger.error(f"SQL programming error on '{self.db_id}': {e}")
            if conn:
                conn.rollback()
            raise ValueError(f"SQL query error: {e}")
        except OperationalError as e:
            logger.error(f"Database operational error on '{self.db_id}': {e}")
            raise ConnectionError(f"Database connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error executing query on '{self.db_id}': {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.release_connection(conn)
    
    def close(self):
        """Close all connections in the pool"""
        if hasattr(self, 'pool') and self.pool:
            self.pool.closeall()
            logger.info(f"Closed PostgreSQL connection pool for '{self.db_id}'")
