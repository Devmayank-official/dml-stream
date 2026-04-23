"""
Configuration Repository.

SQLite-based repository for application configuration settings
with support for layered loading and validation.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from dml_stream.exceptions.storage import RepositoryError
from dml_stream.storage.database import Database


class ConfigRepository:
    """
    Repository for configuration persistence.
    
    Provides CRUD operations for application configuration
    with support for JSON-based settings storage.
    """

    def __init__(self, db: Database, config_file: Optional[Path] = None) -> None:
        """
        Initialize configuration repository.
        
        Args:
            db: Database connection manager.
            config_file: Optional path to JSON config file for fallback.
        """
        self.db = db
        self.config_file = config_file

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "SELECT value FROM config WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row["value"])
                return default
        except Exception as e:
            raise RepositoryError(f"Failed to get config '{key}': {e}", "config")

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key.
            value: Configuration value (must be JSON-serializable).
            
        Raises:
            RepositoryError: If update fails.
        """
        try:
            value_json = json.dumps(value)
            
            with self.db as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO config (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (key, value_json),
                )
                conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to set config '{key}': {e}", "config")

    def delete(self, key: str) -> bool:
        """
        Delete a configuration key.
        
        Args:
            key: Configuration key to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "DELETE FROM config WHERE key = ?", (key,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise RepositoryError(f"Failed to delete config '{key}': {e}", "config")

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all configuration key-value pairs.
        """
        try:
            with self.db as conn:
                cursor = conn.execute("SELECT key, value FROM config")
                rows = cursor.fetchall()
                return {row["key"]: json.loads(row["value"]) for row in rows}
        except Exception as e:
            raise RepositoryError(f"Failed to get all config: {e}", "config")

    def clear(self) -> int:
        """
        Clear all configuration values.
        
        Returns:
            Number of records deleted.
        """
        try:
            with self.db as conn:
                cursor = conn.execute("DELETE FROM config")
                count = cursor.rowcount
                conn.commit()
                return count
        except Exception as e:
            raise RepositoryError(f"Failed to clear config: {e}", "config")

    def load_from_file(self, config_file: Path) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to JSON configuration file.
            
        Returns:
            Dictionary of configuration values.
            
        Raises:
            RepositoryError: If file cannot be read or parsed.
        """
        try:
            if not config_file.exists():
                return {}
            
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RepositoryError(f"Config file is corrupted: {e}", str(config_file))
        except Exception as e:
            raise RepositoryError(f"Failed to load config file: {e}", str(config_file))

    def save_to_file(self, config_file: Path, config: Dict[str, Any]) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config_file: Path to JSON configuration file.
            config: Configuration dictionary to save.
            
        Raises:
            RepositoryError: If file cannot be written.
        """
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise RepositoryError(f"Failed to save config file: {e}", str(config_file))

    def exists(self, key: str) -> bool:
        """Check if a configuration key exists."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM config WHERE key = ? LIMIT 1", (key,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            raise RepositoryError(f"Failed to check config key: {e}", "config")

    def count(self) -> int:
        """Get number of configuration entries."""
        try:
            with self.db as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM config")
                return cursor.fetchone()[0]
        except Exception as e:
            raise RepositoryError(f"Failed to count config entries: {e}", "config")
