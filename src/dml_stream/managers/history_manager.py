"""
History manager for tracking download history.

This manager handles:
- Recording completed downloads
- Querying download history
- Statistics and reporting
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from dml_stream.models.entities import DownloadHistory
from dml_stream.models.repositories import HistoryRepository

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Manager for download history operations.
    
    Provides functionality for recording, querying, and
    reporting on download history.
    """
    
    def __init__(self, persist_path: Optional[str] = None) -> None:
        """
        Initialize the history manager.
        
        Args:
            persist_path: Path for persistence file.
        """
        self._repository = HistoryRepository(persist_path or "download_history.json")
    
    def record_download(
        self,
        title: str,
        url: str,
        file_path: str,
        download_type: str = "video",
        status: str = "success"
    ) -> DownloadHistory:
        """
        Record a download in history.
        
        Args:
            title: Title of downloaded content.
            url: Original YouTube URL.
            file_path: Path to downloaded file.
            download_type: Type of download.
            status: Download status.
            
        Returns:
            Recorded DownloadHistory entry.
        """
        entry = self._repository.add_entry(
            title=title,
            url=url,
            file_path=file_path,
            download_type=download_type,
            status=status
        )
        
        logger.debug(f"Recorded download history: {title}")
        return entry
    
    def get_all_history(self) -> List[DownloadHistory]:
        """Get all download history entries."""
        return self._repository.get_all()
    
    def get_recent(self, limit: int = 10) -> List[DownloadHistory]:
        """
        Get most recent downloads.
        
        Args:
            limit: Maximum number of entries to return.
            
        Returns:
            List of recent download history entries.
        """
        return self._repository.get_recent(limit)
    
    def get_by_url(self, url: str) -> List[DownloadHistory]:
        """
        Get history entries by URL.
        
        Args:
            url: YouTube URL to search for.
            
        Returns:
            List of matching history entries.
        """
        return self._repository.get_by_url(url)
    
    def get_by_type(self, download_type: str) -> List[DownloadHistory]:
        """
        Get history entries by download type.
        
        Args:
            download_type: Type to filter by ('video', 'audio', 'playlist').
            
        Returns:
            List of matching history entries.
        """
        return self._repository.get_by_type(download_type)
    
    def get_failed(self) -> List[DownloadHistory]:
        """Get all failed downloads."""
        return self._repository.get_failed()
    
    def search(self, query: str) -> List[DownloadHistory]:
        """
        Search history by title or URL.
        
        Args:
            query: Search query.
            
        Returns:
            List of matching history entries.
        """
        return self._repository.search(query)
    
    def has_downloaded(self, url: str) -> bool:
        """
        Check if a URL has been downloaded before.
        
        Args:
            url: YouTube URL to check.
            
        Returns:
            True if URL exists in history.
        """
        entries = self.get_by_url(url)
        return len(entries) > 0
    
    def get_last_download(self, url: str) -> Optional[DownloadHistory]:
        """
        Get the most recent download for a URL.
        
        Args:
            url: YouTube URL.
            
        Returns:
            Most recent history entry or None.
        """
        entries = self.get_by_url(url)
        if not entries:
            return None
        
        # Sort by date and return most recent
        entries.sort(key=lambda x: x.download_date, reverse=True)
        return entries[0]
    
    def get_statistics(self) -> Dict:
        """
        Get download history statistics.
        
        Returns:
            Dictionary with statistics.
        """
        all_history = self.get_all_history()
        
        # Count by type
        by_type = {}
        for entry in all_history:
            by_type[entry.download_type] = by_type.get(entry.download_type, 0) + 1
        
        # Count by status
        by_status = {}
        for entry in all_history:
            by_status[entry.status] = by_status.get(entry.status, 0) + 1
        
        # Calculate total size (approximate)
        total_size_bytes = 0
        for entry in all_history:
            if entry.status == 'success' and entry.file_size:
                try:
                    # Parse file size string (e.g., "150.25MB")
                    size_str = entry.file_size.upper()
                    if 'GB' in size_str:
                        total_size_bytes += float(size_str.replace('GB', '')) * 1024 * 1024 * 1024
                    elif 'MB' in size_str:
                        total_size_bytes += float(size_str.replace('MB', '')) * 1024 * 1024
                    elif 'KB' in size_str:
                        total_size_bytes += float(size_str.replace('KB', '')) * 1024
                    elif 'B' in size_str:
                        total_size_bytes += float(size_str.replace('B', ''))
                except (ValueError, AttributeError):
                    pass
        
        # Convert to human readable
        if total_size_bytes >= 1024 ** 3:
            total_size = f"{total_size_bytes / (1024 ** 3):.2f} GB"
        elif total_size_bytes >= 1024 ** 2:
            total_size = f"{total_size_bytes / (1024 ** 2):.2f} MB"
        elif total_size_bytes >= 1024:
            total_size = f"{total_size_bytes / 1024:.2f} KB"
        else:
            total_size = f"{total_size_bytes:.2f} B"
        
        # Get date range
        dates = [entry.download_date for entry in all_history if entry.download_date]
        first_download = min(dates) if dates else None
        last_download = max(dates) if dates else None
        
        return {
            'total_downloads': len(all_history),
            'successful': by_status.get('success', 0),
            'failed': by_status.get('failed', 0),
            'by_type': by_type,
            'total_size': total_size,
            'total_size_bytes': total_size_bytes,
            'first_download': first_download,
            'last_download': last_download,
        }
    
    def get_downloads_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[DownloadHistory]:
        """
        Get downloads within a date range.
        
        Args:
            start_date: Start date.
            end_date: End date.
            
        Returns:
            List of downloads in range.
        """
        all_history = self.get_all_history()
        filtered = []
        
        for entry in all_history:
            try:
                entry_date = datetime.strptime(entry.download_date, "%Y-%m-%d %H:%M:%S")
                if start_date <= entry_date <= end_date:
                    filtered.append(entry)
            except (ValueError, TypeError):
                pass
        
        return filtered
    
    def get_downloads_today(self) -> List[DownloadHistory]:
        """Get downloads from today."""
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_downloads_by_date_range(start, now)
    
    def get_downloads_this_week(self) -> List[DownloadHistory]:
        """Get downloads from this week."""
        now = datetime.now()
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_downloads_by_date_range(start, now)
    
    def get_downloads_this_month(self) -> List[DownloadHistory]:
        """Get downloads from this month."""
        now = datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.get_downloads_by_date_range(start, now)
    
    def clear_history(self) -> int:
        """
        Clear all download history.
        
        Returns:
            Number of entries cleared.
        """
        all_history = self.get_all_history()
        count = len(all_history)
        self._repository.clear()
        logger.info(f"Cleared {count} download history entries")
        return count
    
    def remove_failed(self) -> int:
        """
        Remove all failed downloads from history.
        
        Returns:
            Number of entries removed.
        """
        failed = self.get_failed()
        all_history = self.get_all_history()
        
        # Keep only non-failed entries
        to_keep = [h for h in all_history if h.status != 'failed']
        
        # This is inefficient but works with current repository design
        self._repository.clear()
        for entry in to_keep:
            self._repository.add(entry)
        
        removed = len(failed)
        logger.info(f"Removed {removed} failed download entries")
        return removed
    
    def export_to_dict(self) -> List[Dict]:
        """
        Export history as list of dictionaries.
        
        Returns:
            List of history entries as dictionaries.
        """
        all_history = self.get_all_history()
        return [entry.to_dict() for entry in all_history]
    
    def get_unique_videos(self) -> List[DownloadHistory]:
        """
        Get unique videos by URL (deduplicated).
        
        Returns:
            List of unique download entries.
        """
        all_history = self.get_all_history()
        seen_urls = set()
        unique = []
        
        for entry in all_history:
            if entry.url not in seen_urls:
                seen_urls.add(entry.url)
                unique.append(entry)
        
        return unique
