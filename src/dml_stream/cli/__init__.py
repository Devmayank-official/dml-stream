"""
CLI module for YouTube Downloader.

This module provides the command-line interface using Click
and Rich for beautiful terminal output.
"""

from dml_stream.cli.main import cli
from dml_stream.cli.commands import (
    download_video,
    download_audio,
    download_playlist,
    service,
    history,
    config_command,
)

__all__ = [
    "cli",
    "download_video",
    "download_audio",
    "download_playlist",
    "service",
    "history",
    "config_command",
]
