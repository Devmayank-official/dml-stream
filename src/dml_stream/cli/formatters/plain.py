"""
Plain Text Formatter.

Provides simple plain text output for scripting and piping.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console


class PlainFormatter:
    """
    Formatter for plain text output.
    
    Provides simple, unformatted text output suitable for
    scripting, piping, and log files.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        """
        Initialize plain formatter.
        
        Args:
            console: Optional Rich console instance.
        """
        self.console = console or Console()

    def format(self, data: Any) -> str:
        """
        Format data as plain text.
        
        Args:
            data: Data to format.
            
        Returns:
            Plain text string.
        """
        if isinstance(data, dict):
            return self._format_dict(data)
        elif isinstance(data, list):
            return self._format_list(data)
        else:
            return str(data)

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary as key=value pairs."""
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}:")
                lines.append(self.format(value))
            else:
                lines.append(f"{key}={value}")
        return "\n".join(lines)

    def _format_list(self, data: List[Any]) -> str:
        """Format list as newline-separated values."""
        return "\n".join(self.format(item) for item in data)

    def print(self, data: Any) -> None:
        """
        Print data as plain text.
        
        Args:
            data: Data to print.
        """
        text = self.format(data)
        self.console.print(text)

    def print_list(
        self,
        items: List[str],
        separator: str = "\n",
    ) -> None:
        """
        Print list items with separator.
        
        Args:
            items: List of strings to print.
            separator: Item separator.
        """
        self.console.print(separator.join(items))

    def print_key_value(
        self,
        key: str,
        value: str,
        separator: str = ": ",
    ) -> None:
        """
        Print a key-value pair.
        
        Args:
            key: Key/label.
            value: Value.
            separator: Key-value separator.
        """
        self.console.print(f"{key}{separator}{value}")

    def print_header(self, text: str, char: str = "=") -> None:
        """
        Print a header line.
        
        Args:
            text: Header text.
            char: Character to use for line.
        """
        self.console.print(text)
        self.console.print(char * len(text))

    def print_empty(self, message: str = "No data") -> None:
        """
        Print empty data message.
        
        Args:
            message: Message to display.
        """
        self.console.print(message)
