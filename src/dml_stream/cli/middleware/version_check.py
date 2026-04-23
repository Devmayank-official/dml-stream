"""
Version Check Middleware.

Non-blocking update checker that runs asynchronously
to notify users of new versions.
"""

import json
from typing import Optional, Tuple

import requests
from rich.console import Console

from dml_stream.constants.app import __version__ as CURRENT_VERSION
from dml_stream.constants.messages import INFO_PREFIX


class VersionChecker:
    """
    Asynchronous version checker for update notifications.
    
    Checks PyPI for newer versions without blocking CLI startup.
    """

    PYPI_URL = "https://pypi.org/pypi/dml-stream/json"
    TIMEOUT_SECONDS = 2  # Short timeout to avoid blocking

    def __init__(
        self,
        console: Optional[Console] = None,
        current_version: str = CURRENT_VERSION,
    ) -> None:
        """
        Initialize version checker.
        
        Args:
            console: Optional Rich console instance.
            current_version: Current application version.
        """
        self.console = console or Console()
        self.current_version = current_version

    def check_for_updates(self) -> Optional[str]:
        """
        Check for available updates.
        
        Returns:
            New version string if available, None otherwise.
        """
        try:
            response = requests.get(self.PYPI_URL, timeout=self.TIMEOUT_SECONDS)
            response.raise_for_status()
            
            data = response.json()
            latest_version = data["info"]["version"]
            
            if self._is_newer(latest_version, self.current_version):
                return latest_version
            
            return None
            
        except Exception:
            # Silently fail - don't block CLI for update check
            return None

    def check_and_notify(self) -> None:
        """
        Check for updates and notify user if available.
        
        Non-blocking notification displayed after command output.
        """
        new_version = self.check_for_updates()
        
        if new_version:
            self._display_update_message(new_version)

    def _display_update_message(self, new_version: str) -> None:
        """
        Display update available message.
        
        Args:
            new_version: New version string.
        """
        message = (
            f"\n[{INFO_PREFIX}] Update available: "
            f"[bold green]{new_version}[/] "
            f"(you have [bold]{self.current_version}[/])\n"
            f"[dim]Run 'pip install --upgrade dml-stream' to update[/]"
        )
        self.console.print(message)

    def _is_newer(self, latest: str, current: str) -> bool:
        """
        Check if latest version is newer than current.
        
        Args:
            latest: Latest version from PyPI.
            current: Current version.
            
        Returns:
            True if latest is newer.
        """
        try:
            latest_tuple = self._parse_version(latest)
            current_tuple = self._parse_version(current)
            return latest_tuple > current_tuple
        except Exception:
            return False

    def _parse_version(self, version: str) -> Tuple[int, ...]:
        """
        Parse version string to tuple of integers.
        
        Args:
            version: Version string (e.g., "2.5.0").
            
        Returns:
            Tuple of version components.
        """
        # Remove any pre-release suffixes (alpha, beta, rc, etc.)
        version_clean = version.split("-")[0].split("+")[0]
        return tuple(int(x) for x in version_clean.split("."))

    def get_version_info(self) -> dict:
        """
        Get version information dictionary.
        
        Returns:
            Dictionary with version information.
        """
        return {
            "current": self.current_version,
            "latest": self.check_for_updates() or self.current_version,
            "update_available": self._is_newer(
                self.check_for_updates() or self.current_version,
                self.current_version,
            ),
        }
