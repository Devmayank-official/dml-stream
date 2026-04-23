"""
CLI Formatters Package.

Output formatting layer for consistent CLI output across all commands.
Supports multiple output formats: table, JSON, and plain text.
"""

from dml_stream.cli.formatters.table import TableFormatter
from dml_stream.cli.formatters.json_fmt import JSONFormatter
from dml_stream.cli.formatters.plain import PlainFormatter

__all__ = [
    "TableFormatter",
    "JSONFormatter",
    "PlainFormatter",
]
