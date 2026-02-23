"""
Constants for DML Stream.

This module defines all constants used throughout the application
for consistent configuration and maintainability.

Fully cross-platform compatible: Windows, macOS, Linux
"""

from typing import Dict, Any, List, Final
import platform


# =============================================================================
# FORMAT CONSTANTS
# =============================================================================

#: Supported video output formats
VIDEO_FORMATS: Final[List[str]] = [
    'mp4',   # MPEG-4 Part 14 (most compatible)
    'mkv',   # Matroska (feature-rich)
    'avi',   # Audio Video Interleave (legacy)
    'mov',   # QuickTime Movie (Apple)
    'flv',   # Flash Video (legacy)
    'webm',  # Web Media (open format)
    'wmv',   # Windows Media Video
]

#: Supported audio output formats
AUDIO_FORMATS: Final[List[str]] = [
    'mp3',   # MPEG Audio Layer III (most compatible)
    'm4a',   # MPEG-4 Audio (Apple)
    'flac',  # Free Lossless Audio Codec
    'wav',   # Waveform Audio File Format
    'aac',   # Advanced Audio Coding
    'opus',  # Opus Interactive Audio Codec
]

#: Default video format
DEFAULT_VIDEO_FORMAT: Final[str] = 'mp4'

#: Default audio format
DEFAULT_AUDIO_FORMAT: Final[str] = 'mp3'


# =============================================================================
# PLATFORM-SPECIFIC CONSTANTS
# =============================================================================

#: Current platform name
CURRENT_PLATFORM: Final[str] = platform.system()

#: Path separator for current platform
PATH_SEPARATOR: Final[str] = '\\' if platform.system() == 'Windows' else '/'

#: Invalid filename characters (varies by platform)
INVALID_FILENAME_CHARS: Final[str] = '<>:"|?*' if platform.system() == 'Windows' else '/'

#: Maximum path length (Windows has 260 char limit, Unix typically 4096)
MAX_PATH_LENGTH: Final[int] = 260 if platform.system() == 'Windows' else 4096

#: Maximum filename length
MAX_FILENAME_LENGTH: Final[int] = 200 if platform.system() == 'Windows' else 255


# =============================================================================
# DOWNLOAD CONSTANTS
# =============================================================================

#: Maximum number of retry attempts for failed downloads
MAX_RETRIES: Final[int] = 3

#: Default timeout for HTTP requests (seconds)
TIMEOUT_SECONDS: Final[int] = 30

#: Default chunk size for streaming downloads (64 KB)
CHUNK_SIZE: Final[int] = 1024 * 64

#: Size of each chunk for multi-threaded downloads (1 MB)
DOWNLOAD_CHUNK_SIZE: Final[int] = 1024 * 1024

#: Minimum file size to consider for resume (1 KB)
MIN_RESUME_SIZE: Final[int] = 1024

#: Progress update interval (bytes)
PROGRESS_UPDATE_INTERVAL: Final[int] = 1024 * 1024  # 1 MB


# =============================================================================
# THREADING CONSTANTS
# =============================================================================

#: Default number of download threads
DEFAULT_THREADS: Final[int] = 4

#: Maximum number of download threads
MAX_THREADS: Final[int] = 12

#: Minimum number of download threads
MIN_THREADS: Final[int] = 1

#: Maximum concurrent downloads
MAX_CONCURRENT_DOWNLOADS: Final[int] = 3


# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

#: Default configuration values
DEFAULT_CONFIG: Final[Dict[str, Any]] = {
    # Download settings
    'default_output_folder': 'downloads',
    'default_threads': DEFAULT_THREADS,
    'max_threads': MAX_THREADS,
    'min_threads': MIN_THREADS,
    'default_method': 'normal',  # 'normal' or 'fast'
    
    # File paths
    'config_file_path': 'config.json',
    'history_file_path': 'download_history.json',
    'scheduled_downloads_file_path': 'scheduled_downloads.json',
    'batch_downloads_file_path': 'batch_downloads.json',
    'log_file_path': 'app.log.json',
    
    # Log settings
    'log_max_bytes': 10 * 1024 * 1024,  # 10 MB
    'log_backup_count': 5,
    'log_level': 'INFO',
    
    # Feature flags
    'enable_scheduled_downloads': True,
    'enable_batch_downloads': True,
    'enable_process_tracking': True,
    'enable_download_history': True,
    
    # Network settings
    'request_timeout': TIMEOUT_SECONDS,
    'max_retries': MAX_RETRIES,
    'retry_delay': 5,  # seconds
    
    # UI settings
    'enable_rich_console': True,
    'color_theme': 'default',
}

#: Configuration schema for validation
CONFIG_SCHEMA: Final[Dict[str, Dict[str, Any]]] = {
    'default_output_folder': {
        'type': str,
        'required': True,
        'default': 'downloads',
    },
    'default_threads': {
        'type': int,
        'required': True,
        'default': DEFAULT_THREADS,
        'min': MIN_THREADS,
        'max': MAX_THREADS,
    },
    'max_threads': {
        'type': int,
        'required': True,
        'default': MAX_THREADS,
        'min': MIN_THREADS,
    },
    'min_threads': {
        'type': int,
        'required': True,
        'default': MIN_THREADS,
        'min': 1,
    },
    'default_method': {
        'type': str,
        'required': True,
        'default': 'normal',
        'choices': ['normal', 'fast'],
    },
}


# =============================================================================
# SCHEDULER CONSTANTS
# =============================================================================

#: Schedule check interval (seconds)
SCHEDULE_CHECK_INTERVAL: Final[int] = 60

#: Default scheduled download time format
SCHEDULE_TIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

#: Short schedule time format (HH:MM)
SCHEDULE_SHORT_FORMAT: Final[str] = "%H:%M"


# =============================================================================
# PROCESS TRACKING CONSTANTS
# =============================================================================

#: Process status constants
PROCESS_STATUS_RUNNING: Final[str] = 'running'
PROCESS_STATUS_COMPLETED: Final[str] = 'completed'
PROCESS_STATUS_FAILED: Final[str] = 'failed'
PROCESS_STATUS_CANCELLED: Final[str] = 'cancelled'
PROCESS_STATUS_PENDING: Final[str] = 'pending'
PROCESS_STATUS_IN_PROGRESS: Final[str] = 'in_progress'

#: Process types
PROCESS_TYPE_DOWNLOAD: Final[str] = 'download'
PROCESS_TYPE_CONVERSION: Final[str] = 'conversion'
PROCESS_TYPE_MERGE: Final[str] = 'merge'
PROCESS_TYPE_PLAYLIST: Final[str] = 'playlist'


# =============================================================================
# DOWNLOAD TYPE CONSTANTS
# =============================================================================

DOWNLOAD_TYPE_VIDEO: Final[str] = 'video'
DOWNLOAD_TYPE_AUDIO: Final[str] = 'audio'
DOWNLOAD_TYPE_PLAYLIST: Final[str] = 'playlist'

#: All valid download types
VALID_DOWNLOAD_TYPES: Final[List[str]] = [
    DOWNLOAD_TYPE_VIDEO,
    DOWNLOAD_TYPE_AUDIO,
    DOWNLOAD_TYPE_PLAYLIST,
]


# =============================================================================
# STREAM TYPE CONSTANTS
# =============================================================================

STREAM_TYPE_PROGRESSIVE: Final[str] = 'progressive'  # Video + Audio combined
STREAM_TYPE_ADAPTIVE_VIDEO: Final[str] = 'video'      # Video only
STREAM_TYPE_ADAPTIVE_AUDIO: Final[str] = 'audio'      # Audio only


# =============================================================================
# UI CONSTANTS
# =============================================================================

#: Rich console color themes
COLOR_THEMES: Final[Dict[str, Dict[str, str]]] = {
    'default': {
        'primary': 'blue',
        'success': 'green',
        'warning': 'yellow',
        'error': 'red',
        'info': 'cyan',
    },
    'dark': {
        'primary': 'bright_blue',
        'success': 'bright_green',
        'warning': 'bright_yellow',
        'error': 'bright_red',
        'info': 'bright_cyan',
    },
}

#: Progress bar width
PROGRESS_BAR_WIDTH: Final[int] = 40

#: Table styling
TABLE_STYLE: Final[Dict[str, str]] = {
    'header': 'bold magenta',
    'row_alt': 'dim',
    'border': 'blue',
}


# =============================================================================
# FILE AND PATH CONSTANTS
# =============================================================================

#: Invalid filename characters (Windows + Unix)
INVALID_FILENAME_CHARS: Final[str] = '<>:"|?*'

#: Maximum filename length (conservative for cross-platform)
MAX_FILENAME_LENGTH: Final[int] = 200

#: Maximum path length (Windows default)
MAX_PATH_LENGTH: Final[int] = 260


# =============================================================================
# LOGGING CONSTANTS
# =============================================================================

#: Log format for console output
CONSOLE_LOG_FORMAT: Final[str] = (
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

#: Log date format
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

#: Log levels
LOG_LEVELS: Final[Dict[str, int]] = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50,
}


# =============================================================================
# API AND SERVICE CONSTANTS
# =============================================================================

#: YouTube base URLs
YOUTUBE_BASE_URL: Final[str] = 'https://www.youtube.com'
YOUTUBE_WATCH_URL: Final[str] = f'{YOUTUBE_BASE_URL}/watch'
YOUTUBE_SHORT_URL: Final[str] = 'https://youtu.be'

#: User agent for requests
USER_AGENT: Final[str] = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

#: Request headers
DEFAULT_HEADERS: Final[Dict[str, str]] = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
}


# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES: Final[Dict[str, str]] = {
    'ffmpeg_not_found': (
        "FFmpeg is required for this operation but was not found. "
        "Please install FFmpeg from https://ffmpeg.org/download.html"
    ),
    'invalid_url': (
        "Invalid YouTube URL. Please provide a valid YouTube video or playlist URL."
    ),
    'no_streams': (
        "No downloadable streams found for this video."
    ),
    'download_failed': (
        "Download failed. Please check your internet connection and try again."
    ),
    'permission_denied': (
        "Permission denied. Please check file permissions and try again."
    ),
    'disk_full': (
        "Insufficient disk space. Please free up space and try again."
    ),
}
