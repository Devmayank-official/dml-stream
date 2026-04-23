"""
Storage-Related Exceptions.

Exceptions for database operations, repository errors,
and persistence layer failures.
"""

from typing import Optional

from dml_stream.exceptions.base import DMLBaseException


class DatabaseError(DMLBaseException):
    """
    Base exception for database-related errors.
    
    This includes:
    - Connection failures
    - Query execution errors
    - Transaction failures
    - Migration errors
    
    Attributes:
        message: Error message.
        db_path: Optional database file path.
        query: Optional SQL query that failed.
    """

    def __init__(
        self,
        message: str,
        db_path: Optional[str] = None,
        query: Optional[str] = None,
    ) -> None:
        """
        Initialize database error.
        
        Args:
            message: Error message.
            db_path: Optional database path.
            query: Optional SQL query that failed.
        """
        super().__init__(message)
        self.db_path = db_path
        self.query = query


class RepositoryError(DatabaseError):
    """
    Raised when a repository operation fails.
    
    This includes:
    - CRUD operation failures
    - Data serialization errors
    - Repository initialization failures
    
    Attributes:
        message: Error message.
        repository: Optional repository name.
        operation: Optional operation that failed.
    """

    def __init__(
        self,
        message: str,
        repository: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> None:
        """
        Initialize repository error.
        
        Args:
            message: Error message.
            repository: Optional repository name.
            operation: Optional failed operation.
        """
        super().__init__(message)
        self.repository = repository
        self.operation = operation


class IntegrityError(DatabaseError):
    """
    Raised when database integrity constraints are violated.
    
    This includes:
    - Foreign key violations
    - Unique constraint violations
    - NOT NULL constraint violations
    """

    def __init__(
        self,
        message: str,
        constraint: Optional[str] = None,
    ) -> None:
        """
        Initialize integrity error.
        
        Args:
            message: Error message.
            constraint: Optional constraint name.
        """
        super().__init__(message)
        self.constraint = constraint


class MigrationError(DatabaseError):
    """
    Raised when a database migration fails.
    
    This includes:
    - Migration script errors
    - Schema update failures
    - Rollback failures
    """

    def __init__(
        self,
        message: str,
        migration_name: Optional[str] = None,
        version: Optional[int] = None,
    ) -> None:
        """
        Initialize migration error.
        
        Args:
            message: Error message.
            migration_name: Optional migration file name.
            version: Optional migration version.
        """
        super().__init__(message)
        self.migration_name = migration_name
        self.version = version
