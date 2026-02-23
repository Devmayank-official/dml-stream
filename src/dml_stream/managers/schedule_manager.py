"""
Schedule manager for automated download scheduling.

This manager handles:
- Scheduling downloads for specific times
- Running scheduled downloads via daemon
- Managing schedule queue
"""

import logging
import threading
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional

from dml_stream.core.constants import (
    SCHEDULE_CHECK_INTERVAL,
    PROCESS_STATUS_PENDING,
    PROCESS_STATUS_COMPLETED,
    PROCESS_STATUS_FAILED,
)
from dml_stream.models.entities import ScheduledDownload
from dml_stream.models.repositories import ScheduledDownloadRepository

logger = logging.getLogger(__name__)


class ScheduleManager:
    """
    Manager for scheduled download operations.
    
    Provides functionality for scheduling downloads and running
    them automatically via a background daemon thread.
    """
    
    def __init__(
        self,
        persist_path: Optional[str] = None,
        execute_callback: Optional[Callable[[ScheduledDownload], None]] = None
    ) -> None:
        """
        Initialize the schedule manager.
        
        Args:
            persist_path: Path for persistence file.
            execute_callback: Callback for executing scheduled downloads.
        """
        self._repository = ScheduledDownloadRepository(persist_path or "scheduled_downloads.json")
        self._execute_callback = execute_callback
        self._daemon_thread: Optional[threading.Thread] = None
        self._daemon_running = False
        self._lock = threading.RLock()
    
    def schedule_download(
        self,
        url: str,
        download_type: str,
        output_folder: str,
        scheduled_time: str,
        method: str = "normal",
        threads: int = 4,
        output_format: Optional[str] = None,
        max_speed: Optional[float] = None
    ) -> ScheduledDownload:
        """
        Schedule a download for a specific time.
        
        Args:
            url: YouTube URL to download.
            download_type: Type of download ('video', 'audio', 'playlist').
            output_folder: Destination folder.
            scheduled_time: Time in HH:MM or YYYY-MM-DD HH:MM format.
            method: Download method.
            threads: Number of threads.
            output_format: Optional output format.
            max_speed: Optional speed limit.
            
        Returns:
            Created ScheduledDownload instance.
        """
        scheduled = self._repository.add_scheduled(
            url=url,
            download_type=download_type,
            output_folder=output_folder,
            scheduled_time=scheduled_time,
            method=method,
            threads=threads,
            output_format=output_format,
            max_speed=max_speed
        )
        
        logger.info(f"Scheduled download: {url} at {scheduled_time}")
        return scheduled
    
    def get_scheduled(self, scheduled_id: str) -> Optional[ScheduledDownload]:
        """Get a scheduled download by ID."""
        return self._repository.get_by_id(scheduled_id)
    
    def get_all_scheduled(self) -> List[ScheduledDownload]:
        """Get all scheduled downloads."""
        return self._repository.get_all()
    
    def get_pending(self) -> List[ScheduledDownload]:
        """Get all pending scheduled downloads."""
        return self._repository.get_pending()
    
    def get_due(self) -> List[ScheduledDownload]:
        """Get scheduled downloads that are due for execution."""
        return self._repository.get_due()
    
    def cancel_scheduled(self, scheduled_id: str) -> bool:
        """
        Cancel a scheduled download.
        
        Args:
            scheduled_id: ID of scheduled download to cancel.
            
        Returns:
            True if cancelled, False if not found.
        """
        return self._repository.remove_by_id(scheduled_id)
    
    def cancel_all_pending(self) -> int:
        """
        Cancel all pending scheduled downloads.
        
        Returns:
            Number of cancelled downloads.
        """
        return self._repository.cancel_pending()
    
    def update_status(
        self,
        scheduled_id: str,
        status: str,
        completed_at: Optional[str] = None
    ) -> bool:
        """Update status of a scheduled download."""
        return self._repository.update_status(scheduled_id, status, completed_at)
    
    def start_daemon(self) -> bool:
        """
        Start the background daemon thread for processing scheduled downloads.
        
        Returns:
            True if started, False if already running.
        """
        with self._lock:
            if self._daemon_running:
                logger.warning("Daemon already running")
                return False
            
            self._daemon_running = True
            self._daemon_thread = threading.Thread(
                target=self._daemon_loop,
                daemon=True,
                name="ScheduleDaemon"
            )
            self._daemon_thread.start()
            
            logger.info("Schedule daemon started")
            return True
    
    def stop_daemon(self) -> bool:
        """
        Stop the background daemon thread.
        
        Returns:
            True if stopped, False if not running.
        """
        with self._lock:
            if not self._daemon_running:
                return False
            
            self._daemon_running = False
            
            if self._daemon_thread:
                self._daemon_thread.join(timeout=5)
                self._daemon_thread = None
            
            logger.info("Schedule daemon stopped")
            return True
    
    def is_daemon_running(self) -> bool:
        """Check if daemon is running."""
        return self._daemon_running
    
    def _daemon_loop(self) -> None:
        """
        Main daemon loop that checks and executes scheduled downloads.
        """
        logger.info("Daemon loop started")
        
        while self._daemon_running:
            try:
                # Get due scheduled downloads
                due_downloads = self.get_due()
                
                for scheduled in due_downloads:
                    if not self._daemon_running:
                        break
                    
                    try:
                        self._execute_scheduled(scheduled)
                    except Exception as e:
                        logger.error(f"Failed to execute scheduled download {scheduled.id}: {str(e)}")
                        self.update_status(
                            scheduled.id,
                            PROCESS_STATUS_FAILED,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                
                # Sleep until next check
                time.sleep(SCHEDULE_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in daemon loop: {str(e)}")
                time.sleep(SCHEDULE_CHECK_INTERVAL)
        
        logger.info("Daemon loop exited")
    
    def _execute_scheduled(self, scheduled: ScheduledDownload) -> None:
        """
        Execute a scheduled download.
        
        Args:
            scheduled: ScheduledDownload to execute.
        """
        logger.info(f"Executing scheduled download: {scheduled.url}")
        
        # Update status to in-progress
        self.update_status(scheduled.id, "in_progress")
        
        try:
            # Execute via callback
            if self._execute_callback:
                self._execute_callback(scheduled)
                
                # Update status to completed
                self.update_status(
                    scheduled.id,
                    PROCESS_STATUS_COMPLETED,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                logger.info(f"Scheduled download completed: {scheduled.url}")
            else:
                logger.warning("No execute callback configured")
                self.update_status(
                    scheduled.id,
                    PROCESS_STATUS_FAILED,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
        except Exception as e:
            logger.error(f"Scheduled download failed: {str(e)}")
            self.update_status(
                scheduled.id,
                PROCESS_STATUS_FAILED,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            raise
    
    def get_statistics(self) -> Dict:
        """
        Get schedule statistics.
        
        Returns:
            Dictionary with schedule statistics.
        """
        all_scheduled = self.get_all_scheduled()
        pending = self.get_pending()
        due = self.get_due()
        
        return {
            'total': len(all_scheduled),
            'pending': len(pending),
            'due': len(due),
            'daemon_running': self._daemon_running,
        }
    
    def clear_completed(self) -> int:
        """
        Remove all completed/failed scheduled downloads.
        
        Returns:
            Number of removed entries.
        """
        all_scheduled = self.get_all_scheduled()
        to_remove = [
            s for s in all_scheduled
            if s.status in (PROCESS_STATUS_COMPLETED, PROCESS_STATUS_FAILED, PROCESS_STATUS_CANCELLED)
        ]
        
        count = 0
        for scheduled in to_remove:
            if self.cancel_scheduled(scheduled.id):
                count += 1
        
        return count
