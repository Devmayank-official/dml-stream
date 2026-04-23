"""
JSON Output Formatter.

Provides JSON-formatted output for scripting and automation.
"""

import json
from typing import Any, Dict, List, Optional

from rich.console import Console


class JSONFormatter:
    """
    Formatter for JSON output.
    
    Provides clean JSON output for scripting and automation
    with optional pretty-printing.
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> None:
        """
        Initialize JSON formatter.
        
        Args:
            console: Optional Rich console instance.
            indent: JSON indentation level.
            ensure_ascii: Whether to escape non-ASCII characters.
        """
        self.console = console or Console()
        self.indent = indent
        self.ensure_ascii = ensure_ascii

    def format(
        self,
        data: Any,
        pretty: bool = True,
    ) -> str:
        """
        Format data as JSON string.
        
        Args:
            data: Data to format (dict, list, or primitive).
            pretty: Whether to pretty-print.
            
        Returns:
            JSON-formatted string.
        """
        indent = self.indent if pretty else None
        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=self.ensure_ascii,
            default=str,  # Handle datetime and other non-serializable types
        )

    def print(
        self,
        data: Any,
        pretty: bool = True,
    ) -> None:
        """
        Print data as JSON.
        
        Args:
            data: Data to print.
            pretty: Whether to pretty-print.
        """
        json_str = self.format(data, pretty)
        self.console.print(json_str)

    def format_list(
        self,
        items: List[Any],
        keys: Optional[List[str]] = None,
    ) -> str:
        """
        Format a list of items, optionally filtering keys.
        
        Args:
            items: List of dictionaries to format.
            keys: Optional list of keys to include.
            
        Returns:
            JSON-formatted string.
        """
        if keys:
            # Filter each item to only include specified keys
            filtered = [
                {k: item.get(k) for k in keys if k in item}
                for item in items
            ]
            return self.format(filtered)
        
        return self.format(items)

    def format_success(
        self,
        message: str,
        data: Optional[Any] = None,
    ) -> str:
        """
        Format a success response.
        
        Args:
            message: Success message.
            data: Optional data to include.
            
        Returns:
            JSON-formatted success response.
        """
        response = {
            "success": True,
            "message": message,
        }
        if data is not None:
            response["data"] = data
        return self.format(response)

    def format_error(
        self,
        message: str,
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Format an error response.
        
        Args:
            message: Error message.
            error_type: Optional error type/classification.
            details: Optional additional details.
            
        Returns:
            JSON-formatted error response.
        """
        response = {
            "success": False,
            "error": message,
        }
        if error_type:
            response["error_type"] = error_type
        if details:
            response["details"] = details
        return self.format(response)
