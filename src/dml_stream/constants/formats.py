"""
Format Constants.

Supported video/audio formats and conversion settings.
"""

from typing import Final

# =============================================================================
# VIDEO FORMATS
# =============================================================================

#: Supported video output formats
VIDEO_FORMATS: Final[list[str]] = [
    "mp4",   # MPEG-4 Part 14 (most compatible)
    "mkv",   # Matroska (feature-rich)
    "avi",   # Audio Video Interleave (legacy)
    "mov",   # QuickTime Movie (Apple)
    "flv",   # Flash Video (legacy)
    "webm",  # Web Media (open format)
    "wmv",   # Windows Media Video
]

#: Default video format
DEFAULT_VIDEO_FORMAT: Final[str] = "mp4"

#: Video formats that support high quality (1080p+)
HIGH_QUALITY_VIDEO_FORMATS: Final[list[str]] = ["mp4", "mkv", "webm"]

#: Video formats with best compatibility
COMPATIBLE_VIDEO_FORMATS: Final[list[str]] = ["mp4", "avi", "mov"]


# =============================================================================
# AUDIO FORMATS
# =============================================================================

#: Supported audio output formats
AUDIO_FORMATS: Final[list[str]] = [
    "mp3",   # MPEG Audio Layer III (most compatible)
    "m4a",   # MPEG-4 Audio (Apple)
    "flac",  # Free Lossless Audio Codec
    "wav",   # Waveform Audio File Format
    "aac",   # Advanced Audio Coding
    "opus",  # Opus Interactive Audio Codec
]

#: Default audio format
DEFAULT_AUDIO_FORMAT: Final[str] = "mp3"

#: Lossless audio formats
LOSSLESS_AUDIO_FORMATS: Final[list[str]] = ["flac", "wav"]

#: Lossy audio formats
LOSSY_AUDIO_FORMATS: Final[list[str]] = ["mp3", "aac", "m4a", "opus"]

#: Audio formats with best compatibility
COMPATIBLE_AUDIO_FORMATS: Final[list[str]] = ["mp3", "wav", "aac"]


# =============================================================================
# STREAM TYPES
# =============================================================================

#: Progressive stream (video + audio combined)
STREAM_TYPE_PROGRESSIVE: Final[str] = "progressive"

#: Adaptive video-only stream
STREAM_TYPE_VIDEO: Final[str] = "video"

#: Adaptive audio-only stream
STREAM_TYPE_AUDIO: Final[str] = "audio"


# =============================================================================
# RESOLUTION CONSTANTS
# =============================================================================

#: Standard resolutions (height in pixels)
RESOLUTION_4K: Final[int] = 2160
RESOLUTION_1440P: Final[int] = 1440
RESOLUTION_1080P: Final[int] = 1080
RESOLUTION_720P: Final[int] = 720
RESOLUTION_480P: Final[int] = 480
RESOLUTION_360P: Final[int] = 360
RESOLUTION_240P: Final[int] = 240
RESOLUTION_144P: Final[int] = 144

#: Resolution labels
RESOLUTION_LABELS: Final[dict[int, str]] = {
    RESOLUTION_4K: "4K",
    RESOLUTION_1440P: "2K",
    RESOLUTION_1080P: "FHD",
    RESOLUTION_720P: "HD",
    RESOLUTION_480P: "SD",
    RESOLUTION_360P: "360p",
    RESOLUTION_240P: "240p",
    RESOLUTION_144P: "144p",
}


# =============================================================================
# AUDIO BITRATES
# =============================================================================

#: Standard audio bitrates (kbps)
AUDIO_BITRATES: Final[list[int]] = [320, 256, 192, 128, 96, 64]

#: Default audio bitrate
DEFAULT_AUDIO_BITRATE: Final[int] = 192

#: High quality audio bitrate
HIGH_QUALITY_AUDIO_BITRATE: Final[int] = 320

#: Standard audio bitrate
STANDARD_AUDIO_BITRATE: Final[int] = 192

#: Low audio bitrate (for small files)
LOW_AUDIO_BITRATE: Final[int] = 128


# =============================================================================
# FORMAT CODECS
# =============================================================================

#: Video codecs
VIDEO_CODECS: Final[dict[str, str]] = {
    "mp4": "h264",
    "mkv": "h264",
    "webm": "vp9",
    "avi": "h264",
    "mov": "h264",
}

#: Audio codecs
AUDIO_CODECS: Final[dict[str, str]] = {
    "mp3": "libmp3lame",
    "m4a": "aac",
    "flac": "flac",
    "wav": "pcm_s16le",
    "aac": "aac",
    "opus": "libopus",
}

#: Best quality video codec
BEST_VIDEO_CODEC: Final[str] = "h264"

#: Best quality audio codec
BEST_AUDIO_CODEC: Final[str] = "flac"
