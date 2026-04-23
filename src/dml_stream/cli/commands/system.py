"""
System commands for DML Stream.

This module provides system-level commands:
- doctor: Health check and diagnostics
- info: System information
- cleanup: Clean cache and temp files
- update: Self-update via pip
- deps: Verify dependencies
- report: Generate diagnostic report
"""

import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from dml_stream import __version__
from dml_stream.config.settings import Config
from dml_stream.utilities.file_utils import format_file_size, get_available_disk_space, get_total_disk_space
from dml_stream.utilities.platform_utils import get_cache_dir, get_config_dir, get_data_dir, get_system_info

logger = logging.getLogger(__name__)
console = Console()


@click.group("system")
@click.pass_context
def system(ctx: click.Context) -> None:
    """
    System diagnostics and maintenance commands.

    Examples:

        dml-stream system doctor

        dml-stream system info

        dml-stream system report
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = ctx.obj.get('config', Config())


@system.command("doctor")
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show verbose output"
)
@click.pass_context
def system_doctor(ctx: click.Context, verbose: bool) -> None:
    """
    Check system health and diagnose issues.

    Verifies FFmpeg, Python, dependencies, disk space, and network.

    Examples:

        dml-stream system doctor

        dml-stream system doctor --verbose
    """
    console.print(Panel.fit("[bold blue]DML Stream Health Check[/bold blue]"))

    issues: List[str] = []
    warnings: List[str] = []
    checks: List[Tuple[str, bool, str]] = []

    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_ok = sys.version_info >= (3, 9)
    checks.append((
        "Python Version",
        python_ok,
        f"{python_version} (required: 3.9+)"
    ))
    if not python_ok:
        issues.append(f"Python 3.9+ required, found {python_version}")

    # Check FFmpeg
    ffmpeg_path = shutil.which('ffmpeg')
    ffmpeg_ok = ffmpeg_path is not None
    checks.append((
        "FFmpeg",
        ffmpeg_ok,
        ffmpeg_path or "Not found"
    ))
    if not ffmpeg_ok:
        warnings.append("FFmpeg not found - some features will be unavailable")

    # Check required packages
    required_packages = ['click', 'rich', 'pytubefix', 'requests', 'tqdm']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    packages_ok = len(missing_packages) == 0
    checks.append((
        "Required Packages",
        packages_ok,
        "All installed" if packages_ok else f"Missing: {', '.join(missing_packages)}"
    ))
    if not packages_ok:
        issues.append(f"Missing packages: {', '.join(missing_packages)}")

    # Check disk space
    config = ctx.obj.get('config', Config())
    download_folder = config.default_output_folder
    
    # Get disk space (handles non-existent paths robustly)
    available_space = get_available_disk_space(download_folder)
    
    # Check if we have at least 1 GB free
    one_gb = 1024 * 1024 * 1024
    disk_ok = available_space > one_gb if available_space > 0 else True
    
    # Format disk space for display
    if available_space > 0:
        disk_display = format_file_size(available_space)
    else:
        disk_display = "Unable to determine"
    
    checks.append((
        "Disk Space",
        disk_ok,
        disk_display
    ))
    
    if not disk_ok and available_space > 0:
        warnings.append(f"Low disk space ({disk_display} available, < 1 GB)")

    # Check config directory
    config_dir = get_config_dir()
    config_dir_ok = config_dir.exists() or config_dir.parent.exists()
    checks.append((
        "Config Directory",
        config_dir_ok,
        str(config_dir)
    ))
    if not config_dir_ok:
        issues.append(f"Cannot access config directory: {config_dir}")

    # Check write permissions
    try:
        test_file = config_dir / ".write_test"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()
        test_file.unlink()
        write_ok = True
    except Exception:
        write_ok = False

    checks.append((
        "Write Permissions",
        write_ok,
        "OK" if write_ok else "No write access"
    ))
    if not write_ok:
        issues.append("No write permission in config directory")

    # Check network connectivity
    network_ok = check_network_connectivity()
    checks.append((
        "Network",
        network_ok,
        "Connected" if network_ok else "No connection"
    ))
    if not network_ok:
        warnings.append("No internet connection - downloads will fail")

    # Display results
    table = Table(title="Health Check Results", border_style="blue")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    for name, ok, details in checks:
        status = "[green]✓[/green]" if ok else "[red]✗[/red]"
        table.add_row(name, status, details)

    console.print(table)

    # Summary
    console.print()

    if issues:
        console.print(Panel(
            Text("\n".join([f"• {issue}" for issue in issues])),
            title="[bold red]Critical Issues[/bold red]",
            border_style="red"
        ))

    if warnings:
        console.print(Panel(
            Text("\n".join([f"• {warning}" for warning in warnings])),
            title="[bold yellow]Warnings[/bold yellow]",
            border_style="yellow"
        ))

    if not issues and not warnings:
        console.print("[bold green]✓ All checks passed![/bold green]")

    # Exit with error if critical issues
    if issues:
        raise SystemExit(1)

    logger.info(f"Health check completed: {len(issues)} issues, {len(warnings)} warnings")


@system.command("info")
@click.pass_context
def system_info_cmd(ctx: click.Context) -> None:
    """
    Display system and application information.

    Shows OS, Python version, package versions, and DML Stream details.

    Examples:

        dml-stream system info
    """
    # Get system info
    sys_info = get_system_info()

    # Application info
    app_table = Table(title="Application Information")
    app_table.add_column("Property", style="cyan")
    app_table.add_column("Value", style="green")

    app_table.add_row("DML Stream Version", __version__)
    app_table.add_row("Python Version", sys_info['python_version'])
    app_table.add_row("Python Implementation", sys_info['python_implementation'])

    console.print(app_table)

    # System info
    system_table = Table(title="System Information")
    system_table.add_column("Property", style="cyan")
    system_table.add_column("Value", style="white")

    system_table.add_row("Platform", sys_info['platform'].title())
    system_table.add_row("OS", f"{sys_info['system']} {sys_info['release']}")
    system_table.add_row("Architecture", sys_info['machine'])
    system_table.add_row("Processor", sys_info['processor'] or "Unknown")

    console.print(system_table)

    # Package versions
    packages_table = Table(title="Installed Packages")
    packages_table.add_column("Package", style="cyan")
    packages_table.add_column("Version", style="green")

    packages = [
        ('click', 'click'),
        ('rich', 'rich'),
        ('pytubefix', 'pytubefix'),
        ('requests', 'requests'),
        ('tqdm', 'tqdm'),
        ('schedule', 'schedule'),
    ]

    for import_name, package_name in packages:
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'Unknown')
            packages_table.add_row(package_name, version)
        except ImportError:
            packages_table.add_row(package_name, "[red]Not installed[/red]")

    console.print(packages_table)

    # Directory info
    dirs_table = Table(title="Application Directories")
    dirs_table.add_column("Directory", style="cyan")
    dirs_table.add_column("Path", style="dim")

    dirs_table.add_row("Config", str(get_config_dir()))
    dirs_table.add_row("Data", str(get_data_dir()))
    dirs_table.add_row("Cache", str(get_cache_dir()))

    config = ctx.obj.get('config', Config())
    dirs_table.add_row("Downloads", config.default_output_folder)

    console.print(dirs_table)

    logger.info("Displayed system information")


@system.command("cleanup")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be cleaned"
)
@click.pass_context
def system_cleanup(ctx: click.Context, dry_run: bool) -> None:
    """
    Clean cache and temporary files.

    Same as 'storage clean-cache' - removes all cached data.

    Examples:

        dml-stream system cleanup

        dml-stream system cleanup --dry-run
    """
    # Invoke storage clean-cache
    from dml_stream.cli.commands.storage import storage_clean_cache

    console.print("[cyan]Running system cleanup...[/cyan]\n")

    # Create context for storage command
    ctx.invoke(storage_clean_cache, dry_run=dry_run, include_ytdlp=True)


@system.command("update")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be updated"
)
@click.option(
    "--pre",
    is_flag=True,
    help="Include pre-release versions"
)
@click.pass_context
def system_update(ctx: click.Context, dry_run: bool, pre: bool) -> None:
    """
    Self-update DML Stream via pip.

    Checks for updates and upgrades the installation.

    Examples:

        dml-stream system update

        dml-stream system update --dry-run

        dml-stream system update --pre
    """
    console.print(Panel.fit(
        f"[bold]Check for Updates[/bold]\n\n"
        f"[cyan]Current Version:[/cyan] {__version__}\n"
        f"[cyan]Mode:[/cyan] {'Dry Run' if dry_run else 'Will Update'}"
    ))

    try:
        # Check current version on PyPI
        console.print("[cyan]Checking PyPI for latest version...[/cyan]")

        import requests
        response = requests.get("https://pypi.org/pypi/dml-stream/json", timeout=10)

        if response.status_code == 200:
            data = response.json()
            releases = data.get('releases', {})

            # Get latest version
            versions = list(releases.keys())
            if not pre:
                versions = [v for v in versions if 'a' not in v and 'b' not in v and 'rc' not in v]

            if versions:
                latest_version = versions[-1]

                if latest_version == __version__:
                    console.print("[green]✓ You're running the latest version![/green]")
                else:
                    console.print(f"[yellow]New version available: {latest_version}[/yellow]")
                    console.print(f"[dim]Current: {__version__} → Latest: {latest_version}[/dim]\n")

                    if not dry_run:
                        console.print("[cyan]Upgrading...[/cyan]")

                        # Run pip upgrade
                        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "dml-stream"]
                        if pre:
                            cmd.append("--pre")

                        result = subprocess.run(cmd, capture_output=True, text=True)

                        if result.returncode == 0:
                            console.print("[bold green]✓ Update completed![/bold green]")
                            console.print("[dim]Restart the application to use the new version.[/dim]")
                        else:
                            console.print(f"[bold red]Error:[/bold red] {result.stderr}")
                            raise SystemExit(1)
            else:
                console.print("[yellow]Could not determine latest version[/yellow]")
        else:
            console.print("[yellow]Could not connect to PyPI[/yellow]")

    except requests.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Failed to check for updates: {str(e)}")
        logger.error(f"Update check failed: {str(e)}")
        raise SystemExit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Update failed: {str(e)}")
        raise SystemExit(1)

    logger.info(f"Update check completed: current={__version__}")


@system.command("deps")
@click.option(
    "--outdated",
    is_flag=True,
    help="Show only outdated packages"
)
@click.pass_context
def system_deps(ctx: click.Context, outdated: bool) -> None:
    """
    Verify all dependencies are installed and up-to-date.

    Checks installed packages against requirements.

    Examples:

        dml-stream system deps

        dml-stream system deps --outdated
    """
    console.print("[cyan]Checking dependencies...[/cyan]\n")

    # Required dependencies
    required = {
        'click': '8.1.0',
        'rich': '13.0.0',
        'pytubefix': '6.0.0',
        'requests': '2.28.0',
        'tqdm': '4.65.0',
        'schedule': '1.2.0',
    }

    table = Table(title="Dependencies Status", border_style="blue")
    table.add_column("Package", style="cyan")
    table.add_column("Required", style="yellow")
    table.add_column("Installed", style="green")
    table.add_column("Status", style="white")

    outdated_count = 0

    for package, required_version in required.items():
        try:
            module = __import__(package)
            installed_version = getattr(module, '__version__', 'Unknown')

            # Compare versions (simplified)
            if installed_version != 'Unknown':
                status = "[green]✓ OK[/green]"
                if compare_versions(installed_version, required_version) < 0:
                    status = "[yellow]⚠ Outdated[/yellow]"
                    outdated_count += 1
            else:
                status = "[dim]?[/dim]"

            table.add_row(package, required_version, installed_version, status)

        except ImportError:
            table.add_row(package, required_version, "[red]Not installed[/red]", "[red]✗ Missing[/red]")
            outdated_count += 1

    console.print(table)

    if outdated:
        console.print(f"\n[yellow]Found {outdated_count} outdated or missing packages[/yellow]")
    else:
        if outdated_count == 0:
            console.print("\n[bold green]✓ All dependencies are up to date![/bold green]")
        else:
            console.print(f"\n[yellow]Found {outdated_count} packages that need attention[/yellow]")
            console.print("[dim]Run: pip install --upgrade dml-stream[/dim]")

    logger.info(f"Dependency check completed: {outdated_count} issues")


@system.command("report")
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Save report to file"
)
@click.option(
    "--format", "output_format",
    type=click.Choice(['text', 'json', 'markdown']),
    default='text',
    help="Output format"
)
@click.pass_context
def system_report(ctx: click.Context, output: Optional[str], output_format: str) -> None:
    """
    Generate a full diagnostic report.

    Creates a shareable report with system info, configuration, and logs.

    Examples:

        dml-stream system report

        dml-stream system report --format json

        dml-stream system report -o report.md
    """
    console.print("[cyan]Generating diagnostic report...[/cyan]")

    try:
        # Collect report data
        report_data = collect_report_data(ctx.obj.get('config', Config()))

        if output_format == 'json':
            content = json.dumps(report_data, indent=2, default=str)
        elif output_format == 'markdown':
            content = format_report_markdown(report_data)
        else:
            content = format_report_text(report_data)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"[bold green]✓ Report saved to: {output}[/bold green]")
        else:
            console.print()
            console.print(Panel(content, title="Diagnostic Report", border_style="blue"))

        logger.info(f"Generated diagnostic report ({output_format})")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.error(f"Failed to generate report: {str(e)}")
        raise SystemExit(1)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def check_network_connectivity() -> bool:
    """Check if internet connection is available."""
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def compare_versions(v1: str, v2: str) -> int:
    """Compare two version strings. Returns -1, 0, or 1."""
    def normalize(v):
        return [int(x) for x in v.replace('a', '.').replace('b', '.').replace('rc', '.').split('.') if x.isdigit()]

    n1 = normalize(v1)
    n2 = normalize(v2)

    for i in range(max(len(n1), len(n2))):
        a = n1[i] if i < len(n1) else 0
        b = n2[i] if i < len(n2) else 0

        if a < b:
            return -1
        elif a > b:
            return 1

    return 0


def collect_report_data(config: Config) -> Dict[str, Any]:
    """Collect all data for diagnostic report."""
    sys_info = get_system_info()

    return {
        'generated_at': datetime.now().isoformat(),
        'version': __version__,
        'system': {
            'platform': sys_info['platform'],
            'os': f"{sys_info['system']} {sys_info['release']}",
            'architecture': sys_info['machine'],
            'python_version': sys_info['python_version'],
        },
        'configuration': {
            'output_folder': config.default_output_folder,
            'threads': config.default_threads,
            'log_level': config.log_level,
            'features': {
                'scheduled_downloads': config.enable_scheduled_downloads,
                'batch_downloads': config.enable_batch_downloads,
                'history': config.enable_download_history,
            }
        },
        'directories': {
            'config': str(get_config_dir()),
            'data': str(get_data_dir()),
            'cache': str(get_cache_dir()),
        },
        'disk': {
            'total': get_total_disk_space(),
            'available': get_available_disk_space(),
        },
        'dependencies': {
            'click': getattr(__import__('click'), '__version__', 'Unknown'),
            'rich': getattr(__import__('rich'), '__version__', 'Unknown'),
            'pytubefix': getattr(__import__('pytubefix'), '__version__', 'Unknown'),
            'requests': getattr(__import__('requests'), '__version__', 'Unknown'),
            'tqdm': getattr(__import__('tqdm'), '__version__', 'Unknown'),
        },
        'health': {
            'ffmpeg_installed': shutil.which('ffmpeg') is not None,
            'network_connected': check_network_connectivity(),
        }
    }


def format_report_text(data: Dict[str, Any]) -> str:
    """Format report as plain text."""
    lines = [
        "=" * 60,
        "DML STREAM DIAGNOSTIC REPORT",
        "=" * 60,
        f"Generated: {data['generated_at']}",
        f"Version: {data['version']}",
        "",
        "SYSTEM",
        "-" * 40,
        f"Platform: {data['system']['platform']}",
        f"OS: {data['system']['os']}",
        f"Architecture: {data['system']['architecture']}",
        f"Python: {data['system']['python_version']}",
        "",
        "CONFIGURATION",
        "-" * 40,
        f"Output Folder: {data['configuration']['output_folder']}",
        f"Threads: {data['configuration']['threads']}",
        f"Log Level: {data['configuration']['log_level']}",
        "",
        "DEPENDENCIES",
        "-" * 40,
    ]

    for pkg, version in data['dependencies'].items():
        lines.append(f"  {pkg}: {version}")

    lines.extend([
        "",
        "HEALTH CHECK",
        "-" * 40,
        f"FFmpeg: {'✓ Installed' if data['health']['ffmpeg_installed'] else '✗ Not found'}",
        f"Network: {'✓ Connected' if data['health']['network_connected'] else '✗ No connection'}",
        "",
        "=" * 60,
    ])

    return "\n".join(lines)


def format_report_markdown(data: Dict[str, Any]) -> str:
    """Format report as Markdown."""
    lines = [
        "# DML Stream Diagnostic Report",
        "",
        f"**Generated:** {data['generated_at']}",
        f"**Version:** {data['version']}",
        "",
        "## System",
        "",
        f"- **Platform:** {data['system']['platform']}",
        f"- **OS:** {data['system']['os']}",
        f"- **Architecture:** {data['system']['architecture']}",
        f"- **Python:** {data['system']['python_version']}",
        "",
        "## Configuration",
        "",
        f"- **Output Folder:** {data['configuration']['output_folder']}",
        f"- **Threads:** {data['configuration']['threads']}",
        f"- **Log Level:** {data['configuration']['log_level']}",
        "",
        "## Dependencies",
        "",
    ]

    for pkg, version in data['dependencies'].items():
        lines.append(f"- **{pkg}:** {version}")

    lines.extend([
        "",
        "## Health Check",
        "",
        f"- **FFmpeg:** {'✓ Installed' if data['health']['ffmpeg_installed'] else '✗ Not found'}",
        f"- **Network:** {'✓ Connected' if data['health']['network_connected'] else '✗ No connection'}",
    ])

    return "\n".join(lines)
