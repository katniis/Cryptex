"""
Database Connection Handler
Manages MySQL connections using connection pooling
"""

import mysql.connector
from mysql.connector import pooling, Error
from config.database import DB_CONFIG, POOL_CONFIG
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Singleton class to manage database connection pool
    """
    _connection_pool = None

    @classmethod
    def get_pool(cls):
        """
        Get or create connection pool
        
        Returns:
            ConnectionPool: MySQL connection pool
        """
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pooling.MySQLConnectionPool(
                    pool_name=POOL_CONFIG['pool_name'],
                    pool_size=POOL_CONFIG['pool_size'],
                    pool_reset_session=POOL_CONFIG['pool_reset_session'],
                    **DB_CONFIG
                )
                logger.info("✅ Database connection pool created successfully")
            except Error as e:
                logger.error(f"❌ Error creating connection pool: {e}")
                raise
        
        return cls._connection_pool

    @classmethod
    def get_connection(cls):
        """
        Get a connection from the pool
        
        Returns:
            MySQLConnection: Database connection
        """
        try:
            pool = cls.get_pool()
            connection = pool.get_connection()
            return connection
        except Error as e:
            logger.error(f"❌ Error getting connection: {e}")
            raise

    @classmethod
    def close_connection(cls, connection):
        """
        Return connection to pool
        
        Args:
            connection: MySQL connection to close
        """
        if connection and connection.is_connected():
            connection.close()


class Database:
    """
    Database operations helper class
    Provides context manager for automatic connection handling
    """
    
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """
        Context manager entry - gets connection and cursor
        
        Returns:
            tuple: (connection, cursor)
        """
        self.connection = DatabaseConnection.get_connection()
        self.cursor = self.connection.cursor(dictionary=True)
        return self.connection, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - commits and closes connection
        """
        if exc_type:
            # If there was an error, rollback
            if self.connection:
                self.connection.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            # Otherwise commit
            if self.connection:
                self.connection.commit()
        
        # Close cursor and connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            DatabaseConnection.close_connection(self.connection)


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a query and return results
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters
        fetch_one (bool): Fetch single row
        fetch_all (bool): Fetch all rows
        
    Returns:
        Result based on fetch flags, or lastrowid for INSERT
    """
    try:
        with Database() as (conn, cursor):
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                # For INSERT queries, return last inserted ID
                return cursor.lastrowid
                
    except Error as e:
        logger.error(f"❌ Query execution error: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        raise


def execute_many(query, params_list):
    """
    Execute query with multiple parameter sets (bulk insert)
    
    Args:
        query (str): SQL query
        params_list (list): List of parameter tuples
        
    Returns:
        int: Number of rows affected
    """
    try:
        with Database() as (conn, cursor):
            cursor.executemany(query, params_list)
            return cursor.rowcount
            
    except Error as e:
        logger.error(f"❌ Bulk query execution error: {e}")
        raise


def test_connection():
    """
    Test database connection
    
    Returns:
        bool: True if connection successful
    """
    try:
        with Database() as (conn, cursor):
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            logger.info(f"✅ Connected to database: {db_name['DATABASE()']}")
            
            # Show tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logger.info(f"📋 Found {len(tables)} tables")
            
            return True
            
    except Error as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection when run directly
    print("Testing database connection...")
    if test_connection():
        print("\n✅ Database connection is working!")
    else:
        print("\n❌ Database connection failed!")