"""
Table Formatter for Rich Console Output.

Provides Rich table formatting for list commands with
consistent styling and column alignment.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table


class TableFormatter:
    """
    Formatter for Rich table output.
    
    Provides consistent table styling across all list commands
    with support for custom column widths and styles.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        """
        Initialize table formatter.
        
        Args:
            console: Optional Rich console instance.
        """
        self.console = console or Console()

    def format(
        self,
        data: List[Dict[str, Any]],
        columns: List[str],
        title: Optional[str] = None,
        caption: Optional[str] = None,
        column_widths: Optional[Dict[str, int]] = None,
        highlight_column: Optional[str] = None,
    ) -> Table:
        """
        Format data as a Rich table.
        
        Args:
            data: List of dictionaries to display.
            columns: Column headers to display.
            title: Optional table title.
            caption: Optional table caption/footer.
            column_widths: Optional column width overrides.
            highlight_column: Optional column to highlight.
            
        Returns:
            Rich Table object.
        """
        table = Table(
            title=title,
            caption=caption,
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            row_styles=["", "dim"],  # Alternating row styles
        )

        # Add columns
        for col in columns:
            width = column_widths.get(col) if column_widths else None
            table.add_column(col, width=width, overflow="ellipsis")

        # Add rows
        for row in data:
            row_values = []
            for col in columns:
                value = str(row.get(col, ""))
                # Highlight specific column
                if highlight_column and col == highlight_column:
                    value = f"[bold cyan]{value}[/]"
                row_values.append(value)
            table.add_row(*row_values)

        return table

    def print(
        self,
        data: List[Dict[str, Any]],
        columns: List[str],
        title: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> None:
        """
        Print data as a formatted table.
        
        Args:
            data: List of dictionaries to display.
            columns: Column headers.
            title: Optional table title.
            caption: Optional caption.
        """
        table = self.format(data, columns, title, caption)
        self.console.print(table)

    def print_empty(self, message: str = "No data found") -> None:
        """
        Print empty table message.
        
        Args:
            message: Message to display.
        """
        self.console.print(f"[yellow]{message}[/]")

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size for display.
        
        Args:
            size_bytes: Size in bytes.
            
        Returns:
            Formatted size string.
        """
        if not size_bytes:
            return "Unknown"
        
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f}{unit}"
            size /= 1024.0
        return f"{size:.2f}TB"

    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Format duration for display.
        
        Args:
            seconds: Duration in seconds.
            
        Returns:
            Formatted duration string.
        """
        if not seconds:
            return "Unknown"
        
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
