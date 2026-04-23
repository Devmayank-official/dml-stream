"""
Configuration Models.

Pydantic models for application configuration.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """
    Application configuration model.
    
    Validates and stores all application settings
    with type safety and default values.
    """

    # Download settings
    default_output_folder: str = Field(
        default="downloads",
        description="Default folder for downloads",
    )
    default_threads: int = Field(
        default=4,
        ge=1,
        le=12,
        description="Default number of download threads",
    )
    default_method: str = Field(
        default="normal",
        pattern="^(normal|fast)$",
        description="Download method",
    )

    # Format settings
    default_video_format: str = Field(
        default="mp4",
        description="Default video format",
    )
    default_audio_format: str = Field(
        default="mp3",
        description="Default audio format",
    )
    default_quality: str = Field(
        default="best",
        description="Default quality setting",
    )

    # Network settings
    request_timeout: int = Field(
        default=30,
        ge=5,
        description="HTTP request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts",
    )
    retry_delay: int = Field(
        default=5,
        ge=1,
        description="Delay between retries in seconds",
    )

    # Log settings
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )
    log_max_bytes: int = Field(
        default=10485760,
        ge=1024,
        description="Maximum log file size in bytes",
    )
    log_backup_count: int = Field(
        default=5,
        ge=1,
        description="Number of backup log files",
    )

    # Feature flags
    enable_scheduled_downloads: bool = Field(
        default=True,
        description="Enable scheduled downloads",
    )
    enable_batch_downloads: bool = Field(
        default=True,
        description="Enable batch downloads",
    )
    enable_process_tracking: bool = Field(
        default=True,
        description="Enable process tracking",
    )
    enable_download_history: bool = Field(
        default=True,
        description="Enable download history",
    )

    # UI settings
    enable_rich_console: bool = Field(
        default=True,
        description="Enable Rich console output",
    )
    color_theme: str = Field(
        default="default",
        description="Color theme for console output",
    )

    # Database settings
    database_path: Optional[str] = Field(
        default=None,
        description="Path to SQLite database",
    )

    class Config:
        """Pydantic config."""

        extra = "ignore"
        validate_assignment = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Create from dictionary."""
        return cls(**data)

    def update(self, **kwargs: Any) -> "AppConfig":
        """
        Update configuration with new values.
        
        Args:
            **kwargs: Key-value pairs to update.
            
        Returns:
            Updated AppConfig instance.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
