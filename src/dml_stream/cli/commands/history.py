"""
History commands for DML Stream.

This module provides download history management commands.
Preserved from v2.0 with enhancements for v2.5.
"""

import logging
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from dml_stream.config.settings import Config
from dml_stream.managers.history_manager import HistoryManager
from dml_stream.utilities.file_utils import format_file_size

logger = logging.getLogger(__name__)
console = Console()


@click.command("history")
@click.option(
    "--recent", "-r",
    is_flag=True,
    help="Show recent downloads"
)
@click.option(
    "--limit", "-l",
    type=int,
    default=10,
    help="Number of entries to show"
)
@click.option(
    "--search", "-s",
    type=str,
    help="Search history by title or URL"
)
@click.option(
    "--failed",
    is_flag=True,
    help="Show failed downloads"
)
@click.option(
    "--stats",
    is_flag=True,
    help="Show download statistics"
)
@click.option(
    "--export",
    type=click.Path(),
    help="Export history to file"
)
@click.pass_context
def history(
    ctx: click.Context,
    recent: bool,
    limit: int,
    search: str,
    failed: bool,
    stats: bool,
    export: Optional[str]
) -> None:
    """
    View and manage download history.

    Examples:

        dml-stream history --recent

        dml-stream history --stats

        dml-stream history --search "python"

        dml-stream history --export history.json
    """
    config = ctx.obj.get('config', Config())
    manager = HistoryManager(db_path=config.database_path)

    if stats:
        statistics = manager.get_statistics()

        table = Table(title="Download Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Downloads", str(statistics['total_downloads']))
        table.add_row("Successful", str(statistics['successful']))
        table.add_row("Failed", str(statistics['failed']))
        table.add_row("Total Size", statistics['total_size'])

        if statistics['first_download']:
            table.add_row("First Download", statistics['first_download'])
        if statistics['last_download']:
            table.add_row("Last Download", statistics['last_download'])

        console.print(table)

    elif failed:
        entries = manager.get_failed()

        if not entries:
            console.print("[green]No failed downloads[/green]")
        else:
            table = Table(title="Failed Downloads")
            table.add_column("Title")
            table.add_column("URL")
            table.add_column("Date")

            for e in entries[:limit]:
                table.add_row(e.title, e.url, e.download_date)

            console.print(table)

    elif search:
        entries = manager.search(search)

        if not entries:
            console.print(f"[yellow]No results for '{search}'[/yellow]")
        else:
            table = Table(title=f"Search Results: {search}")
            table.add_column("Title")
            table.add_column("Type")
            table.add_column("Status")
            table.add_column("Date")

            for e in entries:
                status_color = "green" if e.status == "success" else "red"
                table.add_row(
                    e.title,
                    e.download_type,
                    f"[{status_color}]{e.status}[/{status_color}]",
                    e.download_date
                )

            console.print(table)

    elif export:
        try:
            import json
            data = manager.export_to_dict()
            with open(export, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            console.print(f"[bold green]✓ History exported to: {export}[/bold green]")
            logger.info(f"History exported to: {export}")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise SystemExit(1)

    else:
        # Show recent by default
        entries = manager.get_recent(limit)

        if not entries:
            console.print("[yellow]No download history[/yellow]")
        else:
            table = Table(title="Recent Downloads")
            table.add_column("Title", style="white")
            table.add_column("Type", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Date", style="dim")

            for e in entries:
                status_color = "green" if e.status == "success" else "red"
                table.add_row(
                    e.title[:40] + "..." if len(e.title) > 40 else e.title,
                    e.download_type,
                    format_file_size(e.file_size) if e.file_size else "0 B",
                    f"[{status_color}]{e.status}[/{status_color}]",
                    e.download_date
                )

            console.print(table)
