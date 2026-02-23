"""
CLI module for YouTube Downloader.

This module provides the command-line interface using Click
and Rich for beautiful terminal output.
"""

from dml_stream.cli.commands import (
    config_command,
    download_audio,
    download_playlist,
    download_video,
    history,
    service,
)
from dml_stream.cli.main import cli

__all__ = [
    "cli",
    "download_video",
    "download_audio",
    "download_playlist",
    "service",
    "history",
    "config_command",
]
