"""
SQLite Database Connection Manager.

Provides a context manager for SQLite database connections with
support for async operations via aiosqlite.

Cross-platform compatible: Windows, macOS, Linux
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from dml_stream.constants.app import DATA_DIR, DATABASE_FILE
from dml_stream.exceptions.storage import DatabaseError


#: Default database path
DEFAULT_DB_PATH: str = str(DATA_DIR / DATABASE_FILE)


class Database:
    """
    SQLite database connection manager.
    
    Manages database connections, migrations, and provides
    a context manager for safe connection handling.
    
    Example:
        with Database(db_path) as db:
            db.execute("SELECT * FROM history")
    """

    def __init__(self, db_path: str) -> None:
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection.
        
        Returns:
            SQLite connection object.
            
        Raises:
            DatabaseError: If connection fails.
        """
        try:
            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect with row factory for dict-like access
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Automatically run migrations
            from dml_stream.constants.app import MIGRATIONS_DIR
            self.run_migrations(MIGRATIONS_DIR)
            
            return self._connection
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}", str(self.db_path))

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> sqlite3.Connection:
        """Context manager entry."""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def execute(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> sqlite3.Cursor:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string.
            params: Optional query parameters.
            
        Returns:
            Cursor object.
            
        Raises:
            DatabaseError: If query execution fails.
        """
        if not self._connection:
            raise DatabaseError("Database not connected", str(self.db_path))
        
        try:
            cursor = self._connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except sqlite3.Error as e:
            raise DatabaseError(f"Query execution failed: {e}", str(self.db_path))

    def commit(self) -> None:
        """
        Commit current transaction.
        
        Raises:
            DatabaseError: If commit fails.
        """
        if not self._connection:
            raise DatabaseError("Database not connected", str(self.db_path))
        
        try:
            self._connection.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Commit failed: {e}", str(self.db_path))

    def executemany(
        self,
        query: str,
        params_list: list[tuple]
    ) -> sqlite3.Cursor:
        """
        Execute a SQL query with multiple parameter sets.
        
        Args:
            query: SQL query string.
            params_list: List of parameter tuples.
            
        Returns:
            Cursor object.
            
        Raises:
            DatabaseError: If execution fails.
        """
        if not self._connection:
            raise DatabaseError("Database not connected", str(self.db_path))
        
        try:
            cursor = self._connection.cursor()
            cursor.executemany(query, params_list)
            return cursor
        except sqlite3.Error as e:
            raise DatabaseError(f"Batch execution failed: {e}", str(self.db_path))

    def run_migrations(self, migrations_dir: Path) -> None:
        """
        Run database migrations from SQL files.
        
        Args:
            migrations_dir: Directory containing migration SQL files.
            
        Raises:
            DatabaseError: If migration fails.
        """
        if not migrations_dir.exists():
            return
        
        # Get migration files in order
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        for migration_file in migration_files:
            try:
                with open(migration_file, "r", encoding="utf-8") as f:
                    sql = f.read()
                
                # Execute migration
                self._connection.executescript(sql)
                self._connection.commit()
                
            except sqlite3.Error as e:
                raise DatabaseError(
                    f"Migration failed: {migration_file.name}: {e}",
                    str(self.db_path)
                )


@contextmanager
def get_database(db_path: Optional[str] = None) -> Generator[Database, None, None]:
    """
    Context manager for database connection.
    
    Args:
        db_path: Path to SQLite database file. Defaults to DATA_DIR/DATABASE_FILE.
        
    Yields:
        Database instance with active connection.
        
    Example:
        with get_database() as db:
            db.execute("SELECT * FROM history")
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    
    db = Database(db_path)
    try:
        db.connect()
        yield db
    finally:
        db.close()
