"""
Configuration CLI commands for DML Stream.

This module provides enhanced configuration commands:
- show: Display current configuration
- set: Set individual configuration values
- reset: Factory reset configuration
- paths: Show all directory paths
- export: Export configuration to file
- import: Import configuration from file
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dml_stream.config.settings import Config
from dml_stream.utilities.platform_utils import get_cache_dir, get_config_dir, get_data_dir

logger = logging.getLogger(__name__)
console = Console()


@click.group("config")
@click.pass_context
def config(ctx: click.Context) -> None:
    """
    Configuration management commands.

    Examples:

        dml-stream config show

        dml-stream config set default_threads 8

        dml-stream config paths

        dml-stream config export config.json
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj.get('config', Config())


@config.command("show")
@click.option(
    "--json", "as_json",
    is_flag=True,
    help="Output as JSON"
)
@click.pass_context
def config_show(ctx: click.Context, as_json: bool) -> None:
    """
    Show current configuration settings.

    Displays all configuration values in a formatted table.

    Examples:

        dml-stream config show

        dml-stream config show --json
    """
    config = ctx.obj.get('config', Config())

    if as_json:
        console.print_json(config.to_json())
    else:
        table = Table(title="Current Configuration", border_style="blue")
        table.add_column("Category", style="cyan")
        table.add_column("Setting", style="white")
        table.add_column("Value", style="green")

        # Group settings by category
        categories = {
            "Download Settings": [
                ("default_output_folder", config.default_output_folder),
                ("default_threads", str(config.default_threads)),
                ("max_threads", str(config.max_threads)),
                ("min_threads", str(config.min_threads)),
                ("default_method", config.default_method),
            ],
            "Logging": [
                ("log_level", config.log_level),
                ("log_max_bytes", f"{config.log_max_bytes / (1024 * 1024):.0f} MB"),
                ("log_backup_count", str(config.log_backup_count)),
            ],
            "Features": [
                ("enable_scheduled_downloads", str(config.enable_scheduled_downloads)),
                ("enable_batch_downloads", str(config.enable_batch_downloads)),
                ("enable_process_tracking", str(config.enable_process_tracking)),
                ("enable_download_history", str(config.enable_download_history)),
            ],
            "Network": [
                ("request_timeout", f"{config.request_timeout}s"),
                ("max_retries", str(config.max_retries)),
                ("retry_delay", f"{config.retry_delay}s"),
            ],
            "UI": [
                ("enable_rich_console", str(config.enable_rich_console)),
                ("color_theme", config.color_theme),
            ],
        }

        for category, settings in categories.items():
            for setting, value in settings:
                table.add_row(category, setting.replace('_', ' ').title(), value)
                category = ""  # Only show category once

        console.print(table)

    logger.info("Displayed configuration")


@config.command("set")
@click.argument("key", type=str)
@click.argument("value", type=str)
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """
    Set a configuration value.

    KEY: Configuration key (e.g., default_threads)

    VALUE: New value

    Examples:

        dml-stream config set default_threads 8

        dml-stream config set log_level DEBUG

        dml-stream config set default_method fast
    """
    config = ctx.obj.get('config', Config())

    if not hasattr(config, key):
        console.print(f"[bold red]Error:[/bold red] Unknown configuration key: {key}")
        console.print("[dim]Use 'dml-stream config show' to see available keys[/dim]")
        raise SystemExit(1)

    # Get current value and convert new value to appropriate type
    current_value = getattr(config, key)
    converted_value: Any = value

    try:
        if isinstance(current_value, int):
            converted_value = int(value)
        elif isinstance(current_value, bool):
            converted_value = value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current_value, float):
            converted_value = float(value)

        # Validate by attempting to set
        config.set(key, converted_value)
        config.save_to_file()

        console.print(f"[bold green]✓ Set {key} = {converted_value}[/bold green]")
        logger.info(f"Configuration updated: {key} = {converted_value}")

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid value for {key}: {value}")
        console.print(f"[dim]Expected type: {type(current_value).__name__}[/dim]")
        logger.error(f"Invalid config value: {key} = {value}")
        raise SystemExit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to set config: {key} = {value}, error: {str(e)}")
        raise SystemExit(1)


@config.command("reset")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt"
)
@click.pass_context
def config_reset(ctx: click.Context, force: bool) -> None:
    """
    Reset configuration to factory defaults.

    Restores all settings to their default values.

    Examples:

        dml-stream config reset

        dml-stream config reset --force
    """
    if not force:
        console.print("[bold yellow]Warning:[/bold yellow] This will reset all configuration to defaults!")
        if not click.confirm("Continue?", default=False):
            console.print("[yellow]Cancelled[/yellow]")
            return

    config = ctx.obj.get('config', Config())
    config.reset_to_defaults()
    config.save_to_file()

    console.print("[bold green]✓ Configuration reset to defaults[/bold green]")
    logger.info("Configuration reset to defaults")


@config.command("paths")
@click.pass_context
def config_paths(ctx: click.Context) -> None:
    """
    Show all directory paths used by the application.

    Displays configuration, data, cache, and downloads directories.

    Examples:

        dml-stream config paths
    """
    config = ctx.obj.get('config', Config())

    # Get platform-specific directories
    config_dir = get_config_dir()
    data_dir = get_data_dir()
    cache_dir = get_cache_dir()

    table = Table(title="Application Directories", border_style="blue")
    table.add_column("Directory", style="cyan")
    table.add_column("Path", style="white")
    table.add_column("Exists", style="green")

    directories = [
        ("Config", config_dir, config_dir.exists()),
        ("Data", data_dir, data_dir.exists()),
        ("Cache", cache_dir, cache_dir.exists()),
        ("Downloads", Path(config.default_output_folder), Path(config.default_output_folder).exists()),
        ("Logs", Path(config.log_file_path).parent, Path(config.log_file_path).parent.exists()),
    ]

    for name, path, exists in directories:
        status = "[green]✓[/green]" if exists else "[yellow]✗[/yellow]"
        table.add_row(name, str(path), status)

    console.print(table)

    # Show file paths
    files_table = Table(title="Configuration Files", border_style="blue")
    files_table.add_column("File", style="cyan")
    files_table.add_column("Path", style="white")
    files_table.add_column("Exists", style="green")

    files = [
        ("Config", config.config_file_path),
        ("History", config.history_file_path),
        ("Scheduled Downloads", config.scheduled_downloads_file_path),
        ("Batch Downloads", config.batch_downloads_file_path),
        ("Log File", config.log_file_path),
    ]

    for name, path in files:
        exists = Path(path).exists()
        status = "[green]✓[/green]" if exists else "[dim]✗[/dim]"
        files_table.add_row(name, str(path), status)  # Fixed: was table.add_row

    console.print(files_table)

    logger.info("Displayed directory paths")


@config.command("export")
@click.argument("output_file", type=click.Path())
@click.pass_context
def config_export(ctx: click.Context, output_file: str) -> None:
    """
    Export configuration to a file.

    Creates a portable configuration file that can be imported elsewhere.

    OUTPUT_FILE: Path to export file

    Examples:

        dml-stream config export config.json

        dml-stream config export /path/to/backup.json
    """
    config = ctx.obj.get('config', Config())

    try:
        # Ensure parent directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export configuration
        config_data = config.to_dict()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)

        console.print(f"[bold green]✓ Configuration exported to: {output_file}[/bold green]")
        logger.info(f"Configuration exported to: {output_file}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to export configuration: {str(e)}")
        raise SystemExit(1)


@config.command("import")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing configuration without confirmation"
)
@click.pass_context
def config_import(ctx: click.Context, input_file: str, force: bool) -> None:
    """
    Import configuration from a file.

    Replaces current configuration with imported values.

    INPUT_FILE: Path to configuration file

    Examples:

        dml-stream config import config.json

        dml-stream config import /path/to/backup.json --force
    """
    try:
        # Load configuration file
        with open(input_file, 'r', encoding='utf-8') as f:
            imported_data = json.load(f)

        # Validate it looks like a config
        required_keys = ['default_output_folder', 'default_threads', 'log_level']
        if not all(key in imported_data for key in required_keys):
            console.print("[bold red]Error:[/bold red] Invalid configuration file format")
            raise SystemExit(1)

        if not force:
            console.print("[bold yellow]Warning:[/bold yellow] This will overwrite your current configuration!")
            if not click.confirm("Continue?", default=False):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Apply imported configuration
        config = ctx.obj.get('config', Config())

        for key, value in imported_data.items():
            if hasattr(config, key):
                try:
                    # Type conversion
                    current_value = getattr(config, key)
                    if isinstance(current_value, int) and isinstance(value, (int, float)):
                        value = int(value)
                    elif isinstance(current_value, bool) and isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes')

                    setattr(config, key, value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to import {key}: {str(e)}")

        config.save_to_file()

        console.print(f"[bold green]✓ Configuration imported from: {input_file}[/bold green]")
        logger.info(f"Configuration imported from: {input_file}")

    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid JSON: {str(e)}")
        logger.error(f"Invalid JSON in config import: {str(e)}")
        raise SystemExit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to import configuration: {str(e)}")
        raise SystemExit(1)
