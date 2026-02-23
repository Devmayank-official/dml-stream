"""
Process manager for tracking and managing download operations.

This manager handles:
- Process creation and tracking
- Progress updates
- Process cancellation
- Process history
"""

import logging
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional

from dml_stream.core.constants import (
    PROCESS_STATUS_RUNNING,
    PROCESS_STATUS_COMPLETED,
    PROCESS_STATUS_FAILED,
    PROCESS_STATUS_CANCELLED,
    PROCESS_TYPE_DOWNLOAD,
)
from dml_stream.models.entities import ProcessInfo
from dml_stream.models.repositories import ProcessRepository

logger = logging.getLogger(__name__)


class ProcessManager:
    """
    Manager for tracking and coordinating download processes.
    
    Provides in-memory process tracking with optional persistence
    for audit purposes.
    """
    
    def __init__(self, persist: bool = False, persist_path: Optional[str] = None) -> None:
        """
        Initialize the process manager.
        
        Args:
            persist: Whether to persist process information.
            persist_path: Path for persistence file.
        """
        self._processes: Dict[str, ProcessInfo] = {}
        self._lock = threading.RLock()
        self._persist = persist
        self._repository: Optional[ProcessRepository] = None
        
        if persist and persist_path:
            try:
                self._repository = ProcessRepository(persist_path)
            except Exception as e:
                logger.warning(f"Failed to initialize process repository: {str(e)}")
                self._persist = False
    
    def create_process(
        self,
        name: str,
        url: str,
        download_type: str = "video",
        pid: Optional[int] = None
    ) -> ProcessInfo:
        """
        Create and register a new process.
        
        Args:
            name: Process name/type.
            url: Source URL.
            download_type: Type of download.
            pid: Optional process ID.
            
        Returns:
            Created ProcessInfo instance.
        """
        process = ProcessInfo.create(
            name=name,
            url=url,
            download_type=download_type,
            pid=pid
        )
        
        with self._lock:
            # Use URL + timestamp as unique key
            key = f"{url}_{datetime.now().timestamp()}"
            self._processes[key] = process
        
        logger.debug(f"Created process: {name} for {url}")
        return process
    
    def get_process(self, key: str) -> Optional[ProcessInfo]:
        """
        Get a process by its key.
        
        Args:
            key: Process key.
            
        Returns:
            ProcessInfo or None if not found.
        """
        with self._lock:
            return self._processes.get(key)
    
    def get_all_processes(self) -> List[ProcessInfo]:
        """Get all tracked processes."""
        with self._lock:
            return list(self._processes.values())
    
    def get_running_processes(self) -> List[ProcessInfo]:
        """Get all currently running processes."""
        with self._lock:
            return [
                p for p in self._processes.values()
                if p.status == PROCESS_STATUS_RUNNING
            ]
    
    def get_completed_processes(self) -> List[ProcessInfo]:
        """Get all completed processes."""
        with self._lock:
            return [
                p for p in self._processes.values()
                if p.status == PROCESS_STATUS_COMPLETED
            ]
    
    def get_failed_processes(self) -> List[ProcessInfo]:
        """Get all failed processes."""
        with self._lock:
            return [
                p for p in self._processes.values()
                if p.status == PROCESS_STATUS_FAILED
            ]
    
    def update_progress(
        self,
        process: ProcessInfo,
        progress: float,
        output_path: str = ""
    ) -> None:
        """
        Update process progress.
        
        Args:
            process: Process to update.
            progress: Progress percentage (0-100).
            output_path: Optional output path.
        """
        with self._lock:
            process.update_progress(progress, output_path)
    
    def complete_process(
        self,
        process: ProcessInfo,
        status: str = PROCESS_STATUS_COMPLETED,
        error_message: Optional[str] = None
    ) -> None:
        """
        Mark a process as completed.
        
        Args:
            process: Process to complete.
            status: Final status.
            error_message: Optional error message.
        """
        with self._lock:
            process.complete(status, error_message)
            logger.debug(f"Process completed: {process.name} - {status}")
            
            if self._persist and self._repository:
                try:
                    self._repository.add(process)
                except Exception as e:
                    logger.warning(f"Failed to persist process: {str(e)}")
    
    def fail_process(
        self,
        process: ProcessInfo,
        error_message: str
    ) -> None:
        """
        Mark a process as failed.
        
        Args:
            process: Process to fail.
            error_message: Error message.
        """
        self.complete_process(process, PROCESS_STATUS_FAILED, error_message)
    
    def cancel_process(self, process: ProcessInfo) -> bool:
        """
        Cancel a running process.
        
        Args:
            process: Process to cancel.
            
        Returns:
            True if cancelled, False if not running.
        """
        with self._lock:
            if process.status != PROCESS_STATUS_RUNNING:
                return False
            
            process.complete(PROCESS_STATUS_CANCELLED, "Cancelled by user")
            logger.debug(f"Process cancelled: {process.name}")
            return True
    
    def cancel_all(self) -> int:
        """
        Cancel all running processes.
        
        Returns:
            Number of cancelled processes.
        """
        count = 0
        with self._lock:
            for process in self.get_running_processes():
                if self.cancel_process(process):
                    count += 1
        return count
    
    def remove_process(self, key: str) -> bool:
        """
        Remove a process from tracking.
        
        Args:
            key: Process key.
            
        Returns:
            True if removed, False if not found.
        """
        with self._lock:
            if key in self._processes:
                del self._processes[key]
                return True
            return False
    
    def clear_completed(self) -> int:
        """
        Remove all completed/failed processes from tracking.
        
        Returns:
            Number of removed processes.
        """
        count = 0
        with self._lock:
            to_remove = [
                key for key, p in self._processes.items()
                if p.status in (PROCESS_STATUS_COMPLETED, PROCESS_STATUS_FAILED, PROCESS_STATUS_CANCELLED)
            ]
            for key in to_remove:
                del self._processes[key]
                count += 1
        return count
    
    def get_statistics(self) -> Dict:
        """
        Get process statistics.
        
        Returns:
            Dictionary with process statistics.
        """
        with self._lock:
            all_processes = list(self._processes.values())
            return {
                'total': len(all_processes),
                'running': len(self.get_running_processes()),
                'completed': len(self.get_completed_processes()),
                'failed': len(self.get_failed_processes()),
                'cancelled': len([
                    p for p in all_processes
                    if p.status == PROCESS_STATUS_CANCELLED
                ]),
            }
    
    def get_process_by_url(self, url: str) -> List[ProcessInfo]:
        """
        Get processes by URL.
        
        Args:
            url: URL to search for.
            
        Returns:
            List of matching processes.
        """
        with self._lock:
            return [p for p in self._processes.values() if p.url == url]
    
    def cleanup_stale_processes(self, max_age_minutes: int = 60) -> int:
        """
        Clean up processes that have been running too long.
        
        Args:
            max_age_minutes: Maximum age in minutes.
            
        Returns:
            Number of cleaned up processes.
        """
        count = 0
        now = datetime.now()
        
        with self._lock:
            for key, process in list(self._processes.items()):
                if process.status == PROCESS_STATUS_RUNNING:
                    try:
                        start_time = datetime.strptime(
                            process.start_time,
                            "%Y-%m-%d %H:%M:%S"
                        )
                        age = (now - start_time).total_seconds() / 60
                        
                        if age > max_age_minutes:
                            self.fail_process(process, "Process timed out")
                            count += 1
                    except Exception:
                        pass
        
        return count
