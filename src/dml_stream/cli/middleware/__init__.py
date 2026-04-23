"""
CLI Middleware Package.

Middleware for error handling, version checking, and other cross-cutting concerns.
"""

from dml_stream.cli.middleware.error_handler import ErrorHandler, handle_error
from dml_stream.cli.middleware.version_check import VersionChecker

__all__ = [
    "ErrorHandler",
    "handle_error",
    "VersionChecker",
]
