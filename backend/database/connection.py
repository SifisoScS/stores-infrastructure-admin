"""
SQL Server Database Connection Manager
Handles connection pooling, session management, and database operations
"""

import os
from contextlib import contextmanager
from typing import Optional

import pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseManager:
    """
    SQL Server database connection manager with connection pooling
    and session management
    """

    def __init__(self):
        """Initialize database connection parameters from environment"""
        self.server = os.getenv('SQL_SERVER_HOST', 'localhost')
        self.database = os.getenv('SQL_SERVER_DATABASE', 'DerivcoDurbanFacilities')
        self.username = os.getenv('SQL_SERVER_USERNAME', 'sa')
        self.password = os.getenv('SQL_SERVER_PASSWORD', '')
        self.driver = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
        self.use_windows_auth = os.getenv('SQL_SERVER_USE_WINDOWS_AUTH', 'False').lower() == 'true'

        self.engine: Optional[object] = None
        self.session_factory: Optional[scoped_session] = None

        # Build connection string
        if self.use_windows_auth:
            # Windows Authentication
            self.connection_string = (
                f"mssql+pyodbc://@{self.server}/{self.database}"
                f"?driver={self.driver.replace(' ', '+')}"
                f"&trusted_connection=yes"
            )
        else:
            # SQL Server Authentication
            self.connection_string = (
                f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/"
                f"{self.database}?driver={self.driver.replace(' ', '+')}"
            )

    def initialize(self, echo: bool = False) -> None:
        """
        Initialize database connection and session factory

        Args:
            echo: If True, SQLAlchemy will log all SQL statements
        """
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=echo or os.getenv('SQL_ECHO', 'False').lower() == 'true',
                connect_args={
                    'connect_timeout': 30,
                    'timeout': 30
                }
            )

            # Test connection
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print(f"✓ Successfully connected to SQL Server: {self.database}")

            # Create session factory
            self.session_factory = scoped_session(
                sessionmaker(
                    bind=self.engine,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False
                )
            )

            print(f"✓ Database session factory initialized")

        except Exception as e:
            print(f"✗ Failed to initialize database connection: {e}")
            raise

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions with automatic commit/rollback

        Yields:
            Session: SQLAlchemy session object

        Example:
            with db_manager.get_session() as session:
                user = session.query(User).first()
        """
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_raw_connection(self):
        """
        Get raw pyodbc connection for direct SQL queries

        Returns:
            pyodbc.Connection: Raw database connection

        Example:
            conn = db_manager.get_raw_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Categories")
        """
        if self.use_windows_auth:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )

        return pyodbc.connect(conn_str, timeout=30)

    def execute_query(self, query: str, params: tuple = None):
        """
        Execute a raw SQL query with parameters

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            List of result rows
        """
        with self.get_session() as session:
            result = session.execute(query, params or {})
            return result.fetchall()

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def close(self) -> None:
        """Close all database connections and dispose of engine"""
        if self.session_factory:
            self.session_factory.remove()
        if self.engine:
            self.engine.dispose()
            print("✓ Database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Get or create global database manager instance

    Returns:
        DatabaseManager: Global database manager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def init_database(echo: bool = False) -> DatabaseManager:
    """
    Initialize global database connection

    Args:
        echo: If True, SQLAlchemy will log all SQL statements

    Returns:
        DatabaseManager: Initialized database manager instance
    """
    db_manager = get_db_manager()
    db_manager.initialize(echo=echo)
    return db_manager


# Convenience function for getting sessions
@contextmanager
def get_db_session():
    """
    Convenience context manager for getting database sessions

    Example:
        from backend.database import get_db_session

        with get_db_session() as session:
            items = session.query(InventoryItem).all()
    """
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        yield session