"""
Application Constants.

Core application metadata, paths, and version information.
"""

import os
import platform
from pathlib import Path
from typing import Final

# =============================================================================
# APPLICATION METADATA
# =============================================================================

#: Application name
APP_NAME: Final[str] = "DML Stream: A Scalable, Module-Driven Media Acquisition Framework"

#: Application CLI alias
APP_ALIAS: Final[str] = "dmls"

#: Application version (semantic versioning)
__version__: Final[str] = "2.5.1"

#: Version tuple for comparisons
VERSION: Final[tuple[int, int, int]] = (2, 5, 1)

#: Application description
APP_DESCRIPTION: Final[str] = (
    "A modern, type-safe Python framework designed for high-volume media extraction. "
    "DML Stream leverages a modular manager-pattern to orchestrate complex download batches "
    "and scheduled workloads. With full Docker support and a persistent SQLite storage layer, "
    "it bridges the gap between simple CLI tools and enterprise media ingestion pipelines."
)

#: Author information
APP_AUTHOR: Final[str] = "DML Labs"

#: Author email
APP_EMAIL: Final[str] = "devmayank.inbox@gmail.com"

#: License
APP_LICENSE: Final[str] = "Apache-2.0"


# =============================================================================
# PLATFORM DETECTION
# =============================================================================

#: Current operating system
CURRENT_OS: Final[str] = platform.system()

#: Is Windows?
IS_WINDOWS: Final[bool] = CURRENT_OS == "Windows"

#: Is macOS?
IS_MACOS: Final[bool] = CURRENT_OS == "Darwin"

#: Is Linux?
IS_LINUX: Final[bool] = CURRENT_OS == "Linux"

#: Path separator
PATH_SEPARATOR: Final[str] = "\\" if IS_WINDOWS else "/"

#: Newline character
NEWLINE: Final[str] = "\r\n" if IS_WINDOWS else "\n"


# =============================================================================
# PATH CONSTANTS - CROSS-PLATFORM USER HOME BASED
# =============================================================================

#: User home directory (platform-aware)
USER_HOME: Final[Path] = Path.home()

#: Base directory for all DML Stream data (in user home)
#: Windows: C:\Users\<USERNAME>\DML Labs\DML Stream
#: macOS:   /Users/<USERNAME>/DML Labs/DML Stream
#: Linux:   /home/<USERNAME>/DML Labs/DML Stream
DML_BASE_DIR: Final[Path] = USER_HOME / "DML Labs" / "DML Stream"

#: Data directory (for runtime data, database)
DATA_DIR: Final[Path] = DML_BASE_DIR / "data"

#: Logs directory
LOGS_DIR: Final[Path] = DML_BASE_DIR / "logs"

#: Downloads directory (default output location)
DOWNLOADS_DIR: Final[Path] = DML_BASE_DIR / "downloads"

#: Cache directory
CACHE_DIR: Final[Path] = DML_BASE_DIR / "cache"

#: Configuration directory (user config)
CONFIG_DIR: Final[Path] = DML_BASE_DIR / "config"

#: Virtual environment directory
VENV_DIR: Final[Path] = DML_BASE_DIR / ".venv"

#: Test fixtures directory
TEST_FIXTURES_DIR: Final[Path] = DML_BASE_DIR / "tests" / "fixtures"

#: Environment file location
ENV_FILE: Final[Path] = DML_BASE_DIR / ".env"


# =============================================================================
# FILE CONSTANTS
# =============================================================================

#: Default configuration filename
CONFIG_FILE: Final[str] = "config.json"

#: Default database filename
DATABASE_FILE: Final[str] = "dml_stream.db"

#: Default log filename
LOG_FILE: Final[str] = "dml_stream.log"

#: Example environment file (in project root)
ENV_EXAMPLE_FILE: Final[str] = ".env.example"


# =============================================================================
# PROJECT ROOT (for development only)
# =============================================================================

#: Application root directory (where src/ lives) - for dev only
APP_ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent

#: Source directory - for dev only
SRC_DIR: Final[Path] = APP_ROOT / "src"

#: Package directory - for dev only
PACKAGE_DIR: Final[Path] = SRC_DIR / "dml_stream"

#: Scripts directory - for dev only
SCRIPTS_DIR: Final[Path] = APP_ROOT / "scripts"

#: Tests directory - for dev only
TESTS_DIR: Final[Path] = APP_ROOT / "tests"

#: Docs directory - for dev only
DOCS_DIR: Final[Path] = APP_ROOT / "docs"

#: Migrations directory - for database schema
MIGRATIONS_DIR: Final[Path] = PACKAGE_DIR / "storage" / "migrations"


# =============================================================================
# URL CONSTANTS
# =============================================================================

#: YouTube base URL
YOUTUBE_BASE_URL: Final[str] = "https://www.youtube.com"

#: YouTube watch URL pattern
YOUTUBE_WATCH_URL: Final[str] = f"{YOUTUBE_BASE_URL}/watch"

#: YouTube shorts URL
YOUTUBE_SHORTS_URL: Final[str] = "https://youtube.com/shorts"

#: YouTube embed URL
YOUTUBE_EMBED_URL: Final[str] = "https://www.youtube.com/embed"

#: YouTube video ID pattern
VIDEO_ID_PATTERN: Final[str] = r"(?:v=|/)([a-zA-Z0-9_-]{11})(?:\?|&|/|$)"

#: YouTube URL patterns
YOUTUBE_URL_PATTERNS: Final[list[str]] = [
    f"{YOUTUBE_BASE_URL}/watch",
    YOUTUBE_SHORTS_URL,
    YOUTUBE_EMBED_URL,
    "https://youtu.be",
]


# =============================================================================
# USER AGENT
# =============================================================================

#: Default user agent for HTTP requests
USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
