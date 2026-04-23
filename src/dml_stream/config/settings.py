"""
Configuration settings and management for DML Stream.

This module provides a robust configuration system with:
- Type-safe configuration using dataclasses
- Automatic file persistence (JSON)
- Configuration validation
- Environment variable overrides
- Default value fallbacks
- Cross-platform path handling

Fully cross-platform compatible: Windows, macOS, Linux
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dml_stream.constants.app import (
    CONFIG_DIR,
    DATA_DIR,
    LOGS_DIR,
    DOWNLOADS_DIR,
    CACHE_DIR,
    DATABASE_FILE,
    LOG_FILE,
    CONFIG_FILE,
)
from dml_stream.core.exceptions import ConfigurationError
from dml_stream.utilities.platform_utils import ensure_config_dir


@dataclass
class Config:
    """
    Configuration class for DML Stream settings.
    
    This class manages all application configuration with type safety,
    validation, and automatic persistence.
    
    Attributes:
        default_output_folder: Default directory for downloaded files.
        default_threads: Default number of download threads.
        max_threads: Maximum allowed threads.
        min_threads: Minimum allowed threads.
        default_method: Default download method ('normal' or 'fast').
        config_file_path: Path to configuration file.
        history_file_path: Path to download history file.
        scheduled_downloads_file_path: Path to scheduled downloads file.
        batch_downloads_file_path: Path to batch downloads file.
        log_file_path: Path to log file.
        log_max_bytes: Maximum log file size before rotation.
        log_backup_count: Number of backup log files to keep.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        enable_scheduled_downloads: Enable/disable scheduled downloads.
        enable_batch_downloads: Enable/disable batch downloads.
        enable_process_tracking: Enable/disable process tracking.
        enable_download_history: Enable/disable download history.
        request_timeout: HTTP request timeout in seconds.
        max_retries: Maximum retry attempts for failed requests.
        retry_delay: Delay between retries in seconds.
        enable_rich_console: Enable/disable rich console output.
        color_theme: Color theme for console output.
    """

    # Download settings
    default_output_folder: str = str(DOWNLOADS_DIR)
    default_threads: int = 4
    max_threads: int = 12
    min_threads: int = 1
    default_method: str = "normal"

    # File paths (set to new centralized locations)
    config_file_path: str = str(CONFIG_DIR / CONFIG_FILE)
    database_path: str = str(DATA_DIR / DATABASE_FILE)
    log_file_path: str = str(LOGS_DIR / LOG_FILE)
    cache_dir: str = str(CACHE_DIR)
    history_file_path: str = str(DATA_DIR / "history.json")
    scheduled_downloads_file_path: str = str(DATA_DIR / "scheduled_downloads.json")
    batch_downloads_file_path: str = str(DATA_DIR / "batch_downloads.json")

    # Log settings
    log_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_backup_count: int = 5
    log_level: str = "INFO"

    # Feature flags
    enable_scheduled_downloads: bool = True
    enable_batch_downloads: bool = True
    enable_process_tracking: bool = True
    enable_download_history: bool = True

    # Network settings
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5

    # UI settings
    enable_rich_console: bool = True
    color_theme: str = "default"

    def __post_init__(self) -> None:
        """Validate configuration after initialization and ensure directories exist."""
        # Ensure all directories exist
        self._ensure_directories()
        self._validate()

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        # Create all required directories
        for dir_path in [CONFIG_DIR, DATA_DIR, LOGS_DIR, DOWNLOADS_DIR, CACHE_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure log directory exists
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def _validate(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            ConfigurationError: If any configuration value is invalid.
        """
        # Validate threads
        if not (1 <= self.min_threads <= self.max_threads):
            raise ConfigurationError(
                "min_threads must be less than or equal to max_threads",
                "thread_range"
            )

        if not (self.min_threads <= self.default_threads <= self.max_threads):
            raise ConfigurationError(
                f"default_threads must be between {self.min_threads} and {self.max_threads}",
                "default_threads"
            )

        # Validate method
        if self.default_method not in ('normal', 'fast'):
            raise ConfigurationError(
                f"default_method must be 'normal' or 'fast', got '{self.default_method}'",
                "default_method"
            )

        # Validate log level
        valid_log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        if self.log_level not in valid_log_levels:
            raise ConfigurationError(
                f"log_level must be one of {valid_log_levels}, got '{self.log_level}'",
                "log_level"
            )

        # Validate color theme
        if self.color_theme not in ('default', 'dark'):
            raise ConfigurationError(
                f"color_theme must be 'default' or 'dark', got '{self.color_theme}'",
                "color_theme"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration.
        """
        return asdict(self)

    def to_json(self, indent: int = 4) -> str:
        """
        Convert configuration to JSON string.
        
        Args:
            indent: Number of spaces for JSON indentation.
            
        Returns:
            JSON string representation of configuration.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, path: Optional[str] = None) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            path: Optional path to save to. Uses config_file_path if not provided.
            
        Raises:
            ConfigurationError: If saving fails.
        """
        save_path = Path(path or self.config_file_path)

        try:
            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
        except OSError as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}", "save")
        except Exception as e:
            raise ConfigurationError(f"Unexpected error saving configuration: {str(e)}", "save")

    @classmethod
    def load_from_file(cls, path: Optional[str] = None) -> 'Config':
        """
        Load configuration from a JSON file.
        
        Args:
            path: Optional path to load from. Uses default config_file_path if not provided.
            
        Returns:
            Config instance with loaded values (defaults for missing values).
            
        Raises:
            ConfigurationError: If loading fails or file is corrupted.
        """
        config_dir = ensure_config_dir()
        load_path = Path(path or str(config_dir / "config.json"))

        try:
            if not load_path.exists():
                # Create default config file
                config = cls(config_file_path=str(load_path))
                config.save_to_file()
                return config

            with open(load_path, encoding='utf-8') as f:
                config_data = json.load(f)

            # Create instance with loaded data, keeping defaults for missing values
            config = cls()
            for key, value in config_data.items():
                if hasattr(config, key):
                    # Type conversion for safety
                    field_type = cls.__dataclass_fields__[key].type
                    try:
                        if field_type == int and isinstance(value, (int, float)):
                            value = int(value)
                        elif field_type == bool and isinstance(value, str):
                            value = value.lower() in ('true', '1', 'yes')
                        setattr(config, key, value)
                    except (ValueError, TypeError):
                        # Keep default value if type conversion fails
                        pass

            config.config_file_path = str(load_path)
            return config

        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Configuration file is corrupted: {str(e)}", "parse")
        except OSError as e:
            raise ConfigurationError(f"Failed to read configuration file: {str(e)}", "read")
        except Exception as e:
            raise ConfigurationError(f"Unexpected error loading configuration: {str(e)}", "load")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Create Config instance from dictionary.
        
        Args:
            data: Dictionary with configuration values.
            
        Returns:
            Config instance with provided values.
        """
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config

    @classmethod
    def from_env(cls, prefix: str = "DML_STREAM_") -> 'Config':
        """
        Create Config instance from environment variables.
        
        Environment variables should be prefixed with the specified prefix
        and use uppercase names. For example:
        - DML_STREAM_DEFAULT_OUTPUT_FOLDER=/path/to/downloads
        - DML_STREAM_DEFAULT_THREADS=8
        
        Args:
            prefix: Prefix for environment variables.
            
        Returns:
            Config instance with values from environment variables.
        """
        config = cls()

        for field_name in cls.__dataclass_fields__:
            env_name = f"{prefix}{field_name.upper()}"
            env_value = os.environ.get(env_name)

            if env_value is not None:
                field_type = cls.__dataclass_fields__[field_name].type
                try:
                    if field_type == int:
                        env_value = int(env_value)
                    elif field_type == bool:
                        env_value = env_value.lower() in ('true', '1', 'yes')
                    setattr(config, field_name, env_value)
                except (ValueError, TypeError):
                    # Keep default value if type conversion fails
                    pass

        return config

    def update(self, **kwargs) -> None:
        """
        Update configuration values.
        
        Args:
            **kwargs: Configuration key-value pairs to update.
            
        Raises:
            ConfigurationError: If any update value is invalid.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ConfigurationError(f"Unknown configuration key: {key}", key)

        self._validate()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key doesn't exist.
            
        Returns:
            Configuration value or default.
        """
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key.
            value: Value to set.
            
        Raises:
            ConfigurationError: If key doesn't exist or value is invalid.
        """
        if not hasattr(self, key):
            raise ConfigurationError(f"Unknown configuration key: {key}", key)

        setattr(self, key, value)
        self._validate()

    def reset_to_defaults(self) -> None:
        """Reset all configuration values to defaults."""
        defaults = DEFAULT_CONFIG
        for key, value in defaults.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._set_default_paths()
        self._validate()


class ConfigManager:
    """
    Singleton configuration manager for global configuration access.
    
    This class provides a centralized way to manage configuration across
    the entire application with lazy loading and caching.
    
    Example:
        >>> config = ConfigManager.get_instance()
        >>> print(config.default_threads)
        4
        >>> ConfigManager.update_config(default_threads=8)
        >>> ConfigManager.save()
    """

    _instance: Optional['ConfigManager'] = None
    _config: Optional[Config] = None

    def __new__(cls) -> 'ConfigManager':
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        if self._config is None:
            self._config = Config()

    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """
        Get the singleton instance.
        
        Returns:
            ConfigManager instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_config(cls) -> Config:
        """
        Get the current configuration.
        
        Returns:
            Config instance.
        """
        manager = cls.get_instance()
        return manager._config

    @classmethod
    def load(cls, path: Optional[str] = None) -> Config:
        """
        Load configuration from file.
        
        Args:
            path: Optional path to load from.
            
        Returns:
            Loaded Config instance.
        """
        manager = cls.get_instance()
        manager._config = Config.load_from_file(path)
        return manager._config

    @classmethod
    def save(cls, path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            path: Optional path to save to.
        """
        manager = cls.get_instance()
        if manager._config:
            manager._config.save_to_file(path)

    @classmethod
    def update_config(cls, **kwargs) -> None:
        """
        Update configuration values.
        
        Args:
            **kwargs: Configuration key-value pairs to update.
        """
        manager = cls.get_instance()
        if manager._config:
            manager._config.update(**kwargs)

    @classmethod
    def reset(cls) -> None:
        """Reset configuration to defaults."""
        manager = cls.get_instance()
        manager._config = Config()

    @classmethod
    def reload(cls, path: Optional[str] = None) -> Config:
        """
        Reload configuration from file.
        
        Args:
            path: Optional path to load from.
            
        Returns:
            Reloaded Config instance.
        """
        return cls.load(path)
