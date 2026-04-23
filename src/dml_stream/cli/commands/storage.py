"""
Storage management commands for DML Stream.

This module provides storage management commands:
- status: Disk usage and download folder stats
- analyze: Largest files, duplicates, orphans
- prune: Delete incomplete/temp files
- move: Relocate downloads folder
- clean-cache: Wipe application cache
- dedupe: Find and remove duplicates
"""

import hashlib
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from dml_stream.config.settings import Config
from dml_stream.utilities.file_utils import format_file_size, get_available_disk_space, get_total_disk_space
from dml_stream.utilities.platform_utils import get_cache_dir, get_config_dir, get_data_dir

logger = logging.getLogger(__name__)
console = Console()


@click.group("storage")
@click.pass_context
def storage(ctx: click.Context) -> None:
    """
    Storage management and disk space utilities.

    Examples:

        dml-stream storage status

        dml-stream storage analyze

        dml-stream storage prune

        dml-stream storage clean-cache

        dml-stream storage dedupe
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj.get('config', Config())


@storage.command("status")
@click.pass_context
def storage_status(ctx: click.Context) -> None:
    """
    Show disk usage and download folder statistics.

    Displays available disk space, download folder size, and file counts.

    Examples:

        dml-stream storage status
    """
    try:
        config = ctx.obj.get('config', Config())
        download_folder = config.default_output_folder

        # Get disk info
        total_space = get_total_disk_space(download_folder)
        available_space = get_available_disk_space(download_folder)
        used_space = total_space - available_space if total_space > 0 else 0
        usage_percent = (used_space / total_space * 100) if total_space > 0 else 0

        # Get download folder stats
        folder_size = 0
        file_count = 0
        video_count = 0
        audio_count = 0

        if os.path.exists(download_folder):
            for root, dirs, files in os.walk(download_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        folder_size += size
                        file_count += 1

                        ext = os.path.splitext(file)[1].lower()
                        if ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                            video_count += 1
                        elif ext in ['.mp3', '.m4a', '.flac', '.wav', '.aac']:
                            audio_count += 1
                    except (OSError, IOError):
                        pass

        # Display
        disk_table = Table(title="Disk Usage")
        disk_table.add_column("Metric", style="cyan")
        disk_table.add_column("Value", style="green")
        disk_table.add_column("Percentage", style="yellow")

        disk_table.add_row(
            "Total Space",
            format_file_size(total_space) if total_space > 0 else "Unknown",
            ""
        )
        disk_table.add_row(
            "Used Space",
            format_file_size(used_space) if used_space > 0 else "Unknown",
            f"{usage_percent:.1f}%"
        )
        disk_table.add_row(
            "Available Space",
            format_file_size(available_space) if available_space > 0 else "Unknown",
            f"{100 - usage_percent:.1f}%"
        )

        console.print(disk_table)
        console.print()

        folder_table = Table(title=f"Download Folder: {download_folder}")
        folder_table.add_column("Metric", style="cyan")
        folder_table.add_column("Value", style="green")

        folder_table.add_row("Total Size", format_file_size(folder_size))
        folder_table.add_row("Total Files", str(file_count))
        folder_table.add_row("Video Files", str(video_count))
        folder_table.add_row("Audio Files", str(audio_count))

        console.print(folder_table)

        logger.info("Displayed storage status")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to get storage status: {str(e)}")
        raise SystemExit(1)


@storage.command("analyze")
@click.option(
    "--top", "-t",
    type=int,
    default=10,
    help="Number of largest files to show"
)
@click.option(
    "--find-duplicates",
    is_flag=True,
    help="Find duplicate files"
)
@click.pass_context
def storage_analyze(ctx: click.Context, top: int, find_duplicates: bool) -> None:
    """
    Analyze storage for largest files and duplicates.

    Shows the largest files in your download folder and optionally finds duplicates.

    Examples:

        dml-stream storage analyze

        dml-stream storage analyze --top 20

        dml-stream storage analyze --find-duplicates
    """
    try:
        config = ctx.obj.get('config', Config())
        download_folder = config.default_output_folder

        if not os.path.exists(download_folder):
            console.print("[yellow]Download folder does not exist[/yellow]")
            return

        # Collect all files
        files: List[Tuple[str, int]] = []
        for root, dirs, filenames in os.walk(download_folder):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                try:
                    size = os.path.getsize(file_path)
                    files.append((file_path, size))
                except (OSError, IOError):
                    pass

        if not files:
            console.print("[yellow]No files found in download folder[/yellow]")
            return

        # Sort by size (largest first)
        files.sort(key=lambda x: x[1], reverse=True)

        # Show largest files
        table = Table(title=f"Top {top} Largest Files")
        table.add_column("#", style="dim", width=4)
        table.add_column("File", style="white")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Type", style="cyan")

        for i, (file_path, size) in enumerate(files[:top], 1):
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            table.add_row(
                str(i),
                os.path.basename(file_path)[:50] + "..." if len(os.path.basename(file_path)) > 50 else os.path.basename(file_path),
                format_file_size(size),
                ext.upper()
            )

        console.print(table)
        console.print()

        # Find duplicates if requested
        if find_duplicates:
            console.print("[cyan]Finding duplicates...[/cyan]")

            # Group by size first (quick filter)
            size_groups: Dict[int, List[str]] = {}
            for file_path, size in files:
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(file_path)

            # Check files with same size using hash
            duplicates = []
            for size, paths in size_groups.items():
                if len(paths) > 1:
                    # Calculate hash for each
                    hash_groups: Dict[str, List[str]] = {}
                    for path in paths:
                        try:
                            file_hash = calculate_file_hash(path)
                            if file_hash not in hash_groups:
                                hash_groups[file_hash] = []
                            hash_groups[file_hash].append(path)
                        except Exception:
                            pass

                    # Add groups with duplicates
                    for hash_val, paths_list in hash_groups.items():
                        if len(paths_list) > 1:
                            duplicates.append((size, paths_list))

            if duplicates:
                dup_table = Table(title=f"Found {len(duplicates)} Duplicate Groups")
                dup_table.add_column("Size", style="green")
                dup_table.add_column("Files", style="yellow")

                for size, paths in duplicates:
                    file_list = "\n".join([os.path.basename(p) for p in paths[:3]])
                    if len(paths) > 3:
                        file_list += f"\n... and {len(paths) - 3} more"
                    dup_table.add_row(format_file_size(size), file_list)

                console.print(dup_table)
            else:
                console.print("[green]✓ No duplicates found[/green]")

        logger.info(f"Analyzed storage: {len(files)} files, found {len(duplicates) if find_duplicates else 0} duplicates")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to analyze storage: {str(e)}")
        raise SystemExit(1)


@storage.command("prune")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without actually deleting"
)
@click.option(
    "--include-incomplete",
    is_flag=True,
    help="Also remove incomplete downloads (.part, .tmp)"
)
@click.pass_context
def storage_prune(ctx: click.Context, dry_run: bool, include_incomplete: bool) -> None:
    """
    Delete temporary and incomplete download files.

    Cleans up partial downloads and temporary files.

    Examples:

        dml-stream storage prune

        dml-stream storage prune --dry-run

        dml-stream storage prune --include-incomplete
    """
    try:
        config = ctx.obj.get('config', Config())
        download_folder = config.default_output_folder

        if not os.path.exists(download_folder):
            console.print("[yellow]Download folder does not exist[/yellow]")
            return

        # Find files to prune
        files_to_delete = []

        for root, dirs, files in os.walk(download_folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()

                # Check for temp/incomplete files
                if ext in ['.tmp', '.part', '.download', '.crdownload']:
                    files_to_delete.append(file_path)
                elif include_incomplete and filename.endswith('.part'):
                    files_to_delete.append(file_path)

        if not files_to_delete:
            console.print("[green]✓ No files to prune[/green]")
            return

        # Show what will be deleted
        total_size = sum(os.path.getsize(f) for f in files_to_delete if os.path.exists(f))

        console.print(Panel.fit(
            f"[bold]Files to Prune[/bold]\n\n"
            f"[cyan]Count:[/cyan] {len(files_to_delete)}\n"
            f"[cyan]Total Size:[/cyan] {format_file_size(total_size)}\n"
            f"[cyan]Mode:[/cyan] {'Dry Run' if dry_run else 'Will Delete'}"
        ))

        if not dry_run:
            console.print("[yellow]This action cannot be undone![/yellow]")
            if not click.confirm("Continue?", default=False):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Delete files
        deleted_count = 0
        deleted_size = 0

        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Pruning...", total=len(files_to_delete))

            for file_path in files_to_delete:
                try:
                    size = os.path.getsize(file_path)
                    if not dry_run:
                        os.remove(file_path)
                        deleted_count += 1
                        deleted_size += size
                    progress.update(task, advance=1)
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {str(e)}")

        if dry_run:
            console.print(f"[green]Would delete {len(files_to_delete)} files ({format_file_size(total_size)})[/green]")
        else:
            console.print(f"[bold green]✓ Pruned {deleted_count} files ({format_file_size(deleted_size)})[/bold green]")

        logger.info(f"Pruned {deleted_count} files ({format_file_size(deleted_size)})")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Prune failed: {str(e)}")
        raise SystemExit(1)


@storage.command("move")
@click.argument("destination", type=click.Path())
@click.option(
    "--copy",
    is_flag=True,
    help="Copy instead of move (keep original)"
)
@click.pass_context
def storage_move(ctx: click.Context, destination: str, copy: bool) -> None:
    """
    Relocate the downloads folder to a new destination.

    Updates configuration and optionally moves existing files.

    DESTINATION: New download folder path

    Examples:

        dml-stream storage move /path/to/new/folder

        dml-stream storage move D:\\Downloads --copy
    """
    try:
        config = ctx.obj.get('config', Config())
        old_folder = config.default_output_folder

        # Ensure destination exists
        Path(destination).mkdir(parents=True, exist_ok=True)

        console.print(Panel.fit(
            f"[bold]Move Downloads Folder[/bold]\n\n"
            f"[cyan]From:[/cyan] {old_folder}\n"
            f"[cyan]To:[/cyan] {destination}\n"
            f"[cyan]Mode:[/cyan] {'Copy' if copy else 'Move'}"
        ))

        # Move/copy existing files
        if os.path.exists(old_folder):
            files_count = sum(len(files) for _, _, files in os.walk(old_folder))

            if files_count > 0:
                console.print(f"[cyan]Found {files_count} files to transfer...[/cyan]")

                with Progress(
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    console=console,
                ) as progress:
                    task = progress.add_task("[cyan]Transferring...", total=files_count)

                    for root, dirs, files in os.walk(old_folder):
                        for file in files:
                            src = os.path.join(root, file)
                            rel_path = os.path.relpath(src, old_folder)
                            dst = os.path.join(destination, rel_path)

                            Path(dst).parent.mkdir(parents=True, exist_ok=True)

                            try:
                                if copy:
                                    shutil.copy2(src, dst)
                                else:
                                    shutil.move(src, dst)
                                progress.update(task, advance=1)
                            except Exception as e:
                                logger.warning(f"Failed to transfer {src}: {str(e)}")

        # Update config
        config.default_output_folder = destination
        config.save_to_file()

        console.print(f"[bold green]✓ Downloads folder moved to: {destination}[/bold green]")

        logger.info(f"Moved downloads folder: {old_folder} -> {destination}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to move downloads folder: {str(e)}")
        raise SystemExit(1)


@storage.command("clean-cache")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted"
)
@click.option(
    "--include-ytdlp",
    is_flag=True,
    help="Also clean yt-dlp/pytubefix cache"
)
@click.pass_context
def storage_clean_cache(ctx: click.Context, dry_run: bool, include_ytdlp: bool) -> None:
    """
    Wipe application cache and temporary files.

    Clears cache directories for yt-dlp, pytubefix, and app data.

    Examples:

        dml-stream storage clean-cache

        dml-stream storage clean-cache --dry-run

        dml-stream storage clean-cache --include-ytdlp
    """
    try:
        cache_dirs = []

        # App cache
        app_cache = get_cache_dir()
        if app_cache.exists():
            cache_dirs.append(("Application Cache", app_cache))

        # Config cache
        config_cache = get_config_dir() / "cache"
        if config_cache.exists():
            cache_dirs.append(("Config Cache", config_cache))

        # Data cache
        data_cache = get_data_dir() / "cache"
        if data_cache.exists():
            cache_dirs.append(("Data Cache", data_cache))

        # yt-dlp cache
        if include_ytdlp:
            ytdlp_cache = Path.home() / ".cache" / "yt-dlp"
            if ytdlp_cache.exists():
                cache_dirs.append(("yt-dlp Cache", ytdlp_cache))

            # Windows yt-dlp location
            if os.name == 'nt':
                ytdlp_cache_win = Path.home() / "AppData" / "Local" / "yt-dlp"
                if ytdlp_cache_win.exists():
                    cache_dirs.append(("yt-dlp Cache (Windows)", ytdlp_cache_win))

        if not cache_dirs:
            console.print("[green]✓ No cache directories found[/green]")
            return

        # Calculate total size
        total_size = 0
        total_files = 0

        for name, cache_dir in cache_dirs:
            try:
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                            total_files += 1
                        except (OSError, IOError):
                            pass
            except Exception:
                pass

        console.print(Panel.fit(
            f"[bold]Clean Cache[/bold]\n\n"
            f"[cyan]Directories:[/cyan] {len(cache_dirs)}\n"
            f"[cyan]Total Files:[/cyan] {total_files}\n"
            f"[cyan]Total Size:[/cyan] {format_file_size(total_size)}\n"
            f"[cyan]Mode:[/cyan] {'Dry Run' if dry_run else 'Will Delete'}"
        ))

        if not dry_run:
            if not click.confirm("Continue? This cannot be undone.", default=False):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Clean each directory
        cleaned_size = 0
        cleaned_files = 0

        for name, cache_dir in cache_dirs:
            console.print(f"[cyan]Cleaning {name}...[/cyan]")

            try:
                if dry_run:
                    for root, dirs, files in os.walk(cache_dir):
                        cleaned_files += len(files)
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                cleaned_size += os.path.getsize(file_path)
                            except (OSError, IOError):
                                pass
                else:
                    # Delete directory
                    shutil.rmtree(cache_dir)
                    cleaned_files += sum(len(files) for _, _, files in os.walk(cache_dir.parent)) if cache_dir.parent.exists() else 0

                if not dry_run:
                    console.print(f"[green]✓ Cleaned {name}[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to clean {name}: {str(e)}[/yellow]")
                logger.warning(f"Failed to clean {name}: {str(e)}")

        if dry_run:
            console.print(f"[green]Would clean {cleaned_files} files ({format_file_size(cleaned_size)})[/green]")
        else:
            console.print(f"[bold green]✓ Cache cleaned successfully[/bold green]")

        logger.info(f"Cleaned cache: {cleaned_files} files, {format_file_size(cleaned_size)}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Cache clean failed: {str(e)}")
        raise SystemExit(1)


@storage.command("dedupe")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show duplicates without deleting"
)
@click.option(
    "--keep",
    type=click.Choice(['newest', 'oldest', 'shortest-path']),
    default='newest',
    help="Which duplicate to keep"
)
@click.pass_context
def storage_dedupe(ctx: click.Context, dry_run: bool, keep: str) -> None:
    """
    Find and remove duplicate downloads.

    Identifies duplicate files by content hash and removes them.

    Examples:

        dml-stream storage dedupe

        dml-stream storage dedupe --dry-run

        dml-stream storage dedupe --keep oldest
    """
    try:
        config = ctx.obj.get('config', Config())
        download_folder = config.default_output_folder

        if not os.path.exists(download_folder):
            console.print("[yellow]Download folder does not exist[/yellow]")
            return

        console.print("[cyan]Scanning for duplicates...[/cyan]")

        # Group files by size first
        size_groups: Dict[int, List[str]] = {}
        total_files = 0

        for root, dirs, files in os.walk(download_folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    size = os.path.getsize(file_path)
                    if size not in size_groups:
                        size_groups[size] = []
                    size_groups[size].append(file_path)
                    total_files += 1
                except (OSError, IOError):
                    pass

        console.print(f"[dim]Scanned {total_files} files[/dim]")

        # Find actual duplicates by hash
        duplicates = []

        for size, paths in size_groups.items():
            if len(paths) > 1:
                hash_groups: Dict[str, List[Tuple[str, float]]] = {}

                for path in paths:
                    try:
                        file_hash = calculate_file_hash(path)
                        mtime = os.path.getmtime(path)

                        if file_hash not in hash_groups:
                            hash_groups[file_hash] = []
                        hash_groups[file_hash].append((path, mtime))
                    except Exception as e:
                        logger.warning(f"Failed to hash {path}: {str(e)}")

                # Process groups with duplicates
                for hash_val, path_list in hash_groups.items():
                    if len(path_list) > 1:
                        # Sort by mtime or path length
                        if keep == 'newest':
                            path_list.sort(key=lambda x: x[1], reverse=True)
                        elif keep == 'oldest':
                            path_list.sort(key=lambda x: x[1])
                        elif keep == 'shortest-path':
                            path_list.sort(key=lambda x: len(x[0]))

                        # Keep first, mark rest for deletion
                        keep_path = path_list[0][0]
                        delete_paths = [p[0] for p in path_list[1:]]
                        duplicates.append((size, keep_path, delete_paths))

        if not duplicates:
            console.print("[green]✓ No duplicates found[/green]")
            return

        # Show duplicates
        total_waste = sum(size * len(paths) for size, _, paths in duplicates)

        table = Table(title=f"Found {len(duplicates)} Duplicate Groups")
        table.add_column("Size", style="green")
        table.add_column("Keep", style="cyan")
        table.add_column("Delete", style="red")

        for size, keep_path, delete_paths in duplicates[:10]:  # Show first 10
            table.add_row(
                format_file_size(size),
                os.path.basename(keep_path)[:30],
                f"{len(delete_paths)} files"
            )

        if len(duplicates) > 10:
            console.print(table)
            console.print(f"[dim]... and {len(duplicates) - 10} more groups[/dim]")
        else:
            console.print(table)

        console.print(f"\n[yellow]Total wasted space: {format_file_size(total_waste)}[/yellow]")

        if not dry_run:
            if not click.confirm("Delete duplicates?", default=False):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Delete duplicates
        deleted_count = 0
        deleted_size = 0

        for size, keep_path, delete_paths in duplicates:
            for path in delete_paths:
                try:
                    if not dry_run:
                        os.remove(path)
                    deleted_count += 1
                    deleted_size += size
                except Exception as e:
                    logger.warning(f"Failed to delete {path}: {str(e)}")

        if dry_run:
            console.print(f"[green]Would delete {deleted_count} duplicates ({format_file_size(deleted_size)})[/green]")
        else:
            console.print(f"[bold green]✓ Deleted {deleted_count} duplicates ({format_file_size(deleted_size)})[/bold green]")

        logger.info(f"Deduped: deleted {deleted_count} files, freed {format_file_size(deleted_size)}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Deduplication failed: {str(e)}")
        raise SystemExit(1)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """Calculate hash of a file."""
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)

    return hash_func.hexdigest()
