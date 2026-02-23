"""
Data repositories for YouTube Downloader.

This module provides repository classes for persistent storage and
retrieval of domain entities using JSON file storage.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Generic, List, Optional, TypeVar

from dml_stream.core.exceptions import ConfigurationError
from dml_stream.models.entities import (
    BatchDownload,
    BatchDownloadItem,
    DownloadHistory,
    ProcessInfo,
    ScheduledDownload,
)

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository for JSON file persistence.
    
    Provides common CRUD operations for all repositories.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the repository.
        
        Args:
            file_path: Path to the JSON data file.
        """
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the data file exists, create if necessary."""
        try:
            parent_dir = Path(self.file_path).parent
            if parent_dir and not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)

            if not os.path.exists(self.file_path):
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=4)
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize data file: {str(e)}", self.file_path)

    def _read_data(self) -> List[dict]:
        """Read data from JSON file."""
        try:
            with open(self.file_path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Data file is corrupted: {str(e)}", self.file_path)

    def _write_data(self, data: List[dict]) -> None:
        """Write data to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise ConfigurationError(f"Failed to write data file: {str(e)}", self.file_path)

    @abstractmethod
    def _to_dict(self, entity: T) -> dict:
        """Convert entity to dictionary."""
        pass

    @abstractmethod
    def _from_dict(self, data: dict) -> T:
        """Create entity from dictionary."""
        pass

    def add(self, entity: T) -> None:
        """Add an entity."""
        data = self._read_data()
        data.append(self._to_dict(entity))
        self._write_data(data)

    def get_all(self) -> List[T]:
        """Get all entities."""
        data = self._read_data()
        return [self._from_dict(item) for item in data]

    def clear(self) -> None:
        """Clear all data."""
        self._write_data([])


class HistoryRepository(BaseRepository[DownloadHistory]):
    """
    Repository for download history persistence.
    """

    def _to_dict(self, entity: DownloadHistory) -> dict:
        return entity.to_dict()

    def _from_dict(self, data: dict) -> DownloadHistory:
        return DownloadHistory.from_dict(data)

    def add_entry(
        self,
        title: str,
        url: str,
        file_path: str,
        download_type: str = "video",
        status: str = "success"
    ) -> DownloadHistory:
        """
        Add a new download history entry.
        
        Args:
            title: Title of downloaded content.
            url: Original YouTube URL.
            file_path: Path to downloaded file.
            download_type: Type of download.
            status: Download status.
            
        Returns:
            Created DownloadHistory entry.
        """
        entry = DownloadHistory.create(
            title=title,
            url=url,
            file_path=file_path,
            download_type=download_type,
            status=status
        )
        self.add(entry)
        return entry

    def get_by_url(self, url: str) -> List[DownloadHistory]:
        """Get history entries by URL."""
        all_entries = self.get_all()
        return [entry for entry in all_entries if entry.url == url]

    def get_by_type(self, download_type: str) -> List[DownloadHistory]:
        """Get history entries by download type."""
        all_entries = self.get_all()
        return [entry for entry in all_entries if entry.download_type == download_type]

    def get_failed(self) -> List[DownloadHistory]:
        """Get all failed downloads."""
        all_entries = self.get_all()
        return [entry for entry in all_entries if entry.status == "failed"]

    def get_recent(self, limit: int = 10) -> List[DownloadHistory]:
        """Get most recent downloads."""
        all_entries = self.get_all()
        # Sort by download date descending
        sorted_entries = sorted(
            all_entries,
            key=lambda x: x.download_date,
            reverse=True
        )
        return sorted_entries[:limit]

    def search(self, query: str) -> List[DownloadHistory]:
        """Search history by title or URL."""
        all_entries = self.get_all()
        query_lower = query.lower()
        return [
            entry for entry in all_entries
            if query_lower in entry.title.lower() or query_lower in entry.url.lower()
        ]


class ScheduledDownloadRepository(BaseRepository[ScheduledDownload]):
    """
    Repository for scheduled downloads persistence.
    """

    def _to_dict(self, entity: ScheduledDownload) -> dict:
        return entity.to_dict()

    def _from_dict(self, data: dict) -> ScheduledDownload:
        return ScheduledDownload.from_dict(data)

    def add_scheduled(
        self,
        url: str,
        download_type: str,
        output_folder: str,
        scheduled_time: str,
        method: str = "normal",
        threads: int = 4,
        output_format: Optional[str] = None,
        max_speed: Optional[float] = None,
    ) -> ScheduledDownload:
        """
        Add a new scheduled download.
        
        Returns:
            Created ScheduledDownload entry.
        """
        scheduled = ScheduledDownload.create(
            url=url,
            download_type=download_type,
            output_folder=output_folder,
            scheduled_time=scheduled_time,
            method=method,
            threads=threads,
            output_format=output_format,
            max_speed=max_speed
        )
        self.add(scheduled)
        return scheduled

    def get_by_id(self, scheduled_id: str) -> Optional[ScheduledDownload]:
        """Get scheduled download by ID."""
        all_scheduled = self.get_all()
        for scheduled in all_scheduled:
            if scheduled.id == scheduled_id:
                return scheduled
        return None

    def get_pending(self) -> List[ScheduledDownload]:
        """Get all pending scheduled downloads."""
        all_scheduled = self.get_all()
        return [s for s in all_scheduled if s.status == "pending"]

    def get_due(self) -> List[ScheduledDownload]:
        """Get scheduled downloads that are due for execution."""
        pending = self.get_pending()
        return [s for s in pending if s.is_due()]

    def update_status(
        self,
        scheduled_id: str,
        status: str,
        completed_at: Optional[str] = None
    ) -> bool:
        """
        Update status of a scheduled download.
        
        Returns:
            True if updated successfully.
        """
        data = self._read_data()
        for i, item in enumerate(data):
            if item['id'] == scheduled_id:
                data[i]['status'] = status
                if completed_at:
                    data[i]['completed_at'] = completed_at
                self._write_data(data)
                return True
        return False

    def remove_by_id(self, scheduled_id: str) -> bool:
        """Remove scheduled download by ID."""
        data = self._read_data()
        original_count = len(data)
        data = [item for item in data if item['id'] != scheduled_id]
        if len(data) < original_count:
            self._write_data(data)
            return True
        return False

    def cancel_pending(self) -> int:
        """
        Cancel all pending scheduled downloads.
        
        Returns:
            Number of cancelled downloads.
        """
        data = self._read_data()
        count = 0
        for i, item in enumerate(data):
            if item['status'] == 'pending':
                data[i]['status'] = 'cancelled'
                data[i]['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                count += 1
        if count > 0:
            self._write_data(data)
        return count


class BatchDownloadRepository(BaseRepository[BatchDownload]):
    """
    Repository for batch downloads persistence.
    """

    def _to_dict(self, entity: BatchDownload) -> dict:
        return entity.to_dict()

    def _from_dict(self, data: dict) -> BatchDownload:
        return BatchDownload.from_dict(data)

    def add_batch(
        self,
        name: str,
        items: Optional[List[BatchDownloadItem]] = None
    ) -> BatchDownload:
        """
        Add a new batch download.
        
        Returns:
            Created BatchDownload entry.
        """
        batch = BatchDownload.create(name=name, items=items)
        self.add(batch)
        return batch

    def get_by_id(self, batch_id: str) -> Optional[BatchDownload]:
        """Get batch download by ID."""
        all_batches = self.get_all()
        for batch in all_batches:
            if batch.id == batch_id:
                return batch
        return None

    def update_status(
        self,
        batch_id: str,
        status: str,
        completed_at: Optional[str] = None,
        current_index: Optional[int] = None
    ) -> bool:
        """Update status of a batch download."""
        data = self._read_data()
        for i, item in enumerate(data):
            if item['id'] == batch_id:
                data[i]['status'] = status
                if completed_at:
                    data[i]['completed_at'] = completed_at
                if current_index is not None:
                    data[i]['current_index'] = current_index
                self._write_data(data)
                return True
        return False

    def update_current_index(self, batch_id: str, current_index: int) -> bool:
        """Update current item index for a batch."""
        return self.update_status(batch_id, "in_progress", current_index=current_index)

    def remove_by_id(self, batch_id: str) -> bool:
        """Remove batch download by ID."""
        data = self._read_data()
        original_count = len(data)
        data = [item for item in data if item['id'] != batch_id]
        if len(data) < original_count:
            self._write_data(data)
            return True
        return False


class ProcessRepository(BaseRepository[ProcessInfo]):
    """
    Repository for process tracking persistence.
    
    Note: Processes are primarily tracked in-memory for performance.
    This repository provides optional persistence for audit purposes.
    """

    def _to_dict(self, entity: ProcessInfo) -> dict:
        return entity.to_dict()

    def _from_dict(self, data: dict) -> ProcessInfo:
        return ProcessInfo.from_dict(data)

    def get_running(self) -> List[ProcessInfo]:
        """Get all running processes."""
        all_processes = self.get_all()
        return [p for p in all_processes if p.status == 'running']

    def get_by_status(self, status: str) -> List[ProcessInfo]:
        """Get processes by status."""
        all_processes = self.get_all()
        return [p for p in all_processes if p.status == status]

    def get_failed(self) -> List[ProcessInfo]:
        """Get all failed processes."""
        all_processes = self.get_all()
        return [p for p in all_processes if p.status == 'failed']

    def archive_completed(self, max_age_hours: int = 24) -> int:
        """
        Archive completed processes older than specified age.
        
        Returns:
            Number of archived processes.
        """
        # This would require additional archive storage
        # For now, just return 0 as this is a placeholder
        return 0
