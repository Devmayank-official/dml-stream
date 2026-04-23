"""
DML Stream Constants Package.

Centralized constants for the application, split into logical modules
for better maintainability and separation of concerns.
"""

from dml_stream.constants.app import (
    APP_NAME,
    APP_ALIAS,
    DML_BASE_DIR,
    CONFIG_DIR,
    CACHE_DIR,
    DATA_DIR,
    LOGS_DIR,
    DOWNLOADS_DIR,
    DATABASE_FILE,
    LOG_FILE,
    CONFIG_FILE,
)
from dml_stream.constants.formats import (
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    DEFAULT_VIDEO_FORMAT,
    DEFAULT_AUDIO_FORMAT,
)
from dml_stream.constants.messages import (
    SUCCESS_PREFIX,
    ERROR_PREFIX,
    WARNING_PREFIX,
    INFO_PREFIX,
)

__all__ = [
    # App constants
    "APP_NAME",
    "APP_ALIAS",
    "DML_BASE_DIR",
    "CONFIG_DIR",
    "CACHE_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    "DOWNLOADS_DIR",
    "DATABASE_FILE",
    "LOG_FILE",
    "CONFIG_FILE",
    # Format constants
    "VIDEO_FORMATS",
    "AUDIO_FORMATS",
    "DEFAULT_VIDEO_FORMAT",
    "DEFAULT_AUDIO_FORMAT",
    # Message constants
    "SUCCESS_PREFIX",
    "ERROR_PREFIX",
    "WARNING_PREFIX",
    "INFO_PREFIX",
]
