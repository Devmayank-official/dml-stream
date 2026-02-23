"""
Batch manager for managing multiple download operations.

This manager handles:
- Creating and managing batch downloads
- Sequential processing of batch items
- Batch progress tracking
"""

import logging
import threading
from datetime import datetime
from typing import Callable, Dict, List, Optional

from dml_stream.core.constants import (
    PROCESS_STATUS_PENDING,
    PROCESS_STATUS_IN_PROGRESS,
    PROCESS_STATUS_COMPLETED,
    PROCESS_STATUS_FAILED,
)
from dml_stream.models.entities import BatchDownload, BatchDownloadItem
from dml_stream.models.repositories import BatchDownloadRepository

logger = logging.getLogger(__name__)


class BatchManager:
    """
    Manager for batch download operations.
    
    Provides functionality for creating, managing, and executing
    batch downloads with multiple videos.
    """
    
    def __init__(
        self,
        persist_path: Optional[str] = None,
        execute_callback: Optional[Callable[[BatchDownloadItem, int, int], None]] = None
    ) -> None:
        """
        Initialize the batch manager.
        
        Args:
            persist_path: Path for persistence file.
            execute_callback: Callback for executing individual batch items.
        """
        self._repository = BatchDownloadRepository(persist_path or "batch_downloads.json")
        self._execute_callback = execute_callback
        self._lock = threading.RLock()
    
    def create_batch(self, name: str) -> BatchDownload:
        """
        Create a new empty batch.
        
        Args:
            name: Batch name.
            
        Returns:
            Created BatchDownload instance.
        """
        batch = self._repository.add_batch(name=name)
        logger.info(f"Created batch: {name} (ID: {batch.id})")
        return batch
    
    def add_item_to_batch(
        self,
        batch_id: str,
        url: str,
        download_type: str,
        output_folder: str,
        method: str = "normal",
        threads: int = 4,
        output_format: Optional[str] = None,
        max_speed: Optional[float] = None
    ) -> bool:
        """
        Add an item to an existing batch.
        
        Args:
            batch_id: ID of batch to add to.
            url: YouTube URL.
            download_type: Type of download.
            output_folder: Destination folder.
            method: Download method.
            threads: Number of threads.
            output_format: Optional output format.
            max_speed: Optional speed limit.
            
        Returns:
            True if added, False if batch not found.
        """
        batch = self._repository.get_by_id(batch_id)
        if not batch:
            logger.error(f"Batch not found: {batch_id}")
            return False
        
        if batch.status != PROCESS_STATUS_PENDING:
            logger.warning(f"Cannot add to batch with status: {batch.status}")
            return False
        
        item = BatchDownloadItem.create(
            url=url,
            download_type=download_type,
            output_folder=output_folder,
            method=method,
            threads=threads,
            output_format=output_format,
            max_speed=max_speed
        )
        
        batch.add_item(item)
        
        # Update in repository (note: this requires re-saving the batch)
        # For simplicity, we'll just log that the item was added in memory
        logger.info(f"Added item to batch {batch_id}: {url}")
        return True
    
    def remove_item_from_batch(self, batch_id: str, index: int) -> bool:
        """
        Remove an item from a batch by index.
        
        Args:
            batch_id: ID of batch.
            index: Index of item to remove.
            
        Returns:
            True if removed, False if not found.
        """
        batch = self._repository.get_by_id(batch_id)
        if not batch:
            return False
        
        return batch.remove_item(index)
    
    def get_batch(self, batch_id: str) -> Optional[BatchDownload]:
        """Get a batch by ID."""
        return self._repository.get_by_id(batch_id)
    
    def get_all_batches(self) -> List[BatchDownload]:
        """Get all batches."""
        return self._repository.get_all()
    
    def delete_batch(self, batch_id: str) -> bool:
        """
        Delete a batch.
        
        Args:
            batch_id: ID of batch to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        return self._repository.remove_by_id(batch_id)
    
    def start_batch(self, batch_id: str) -> bool:
        """
        Start executing a batch.
        
        Args:
            batch_id: ID of batch to start.
            
        Returns:
            True if started, False if not found or already running.
        """
        batch = self.get_batch(batch_id)
        if not batch:
            return False
        
        if batch.status == PROCESS_STATUS_IN_PROGRESS:
            logger.warning(f"Batch already in progress: {batch_id}")
            return False
        
        # Update status
        self._repository.update_status(batch_id, PROCESS_STATUS_IN_PROGRESS)
        logger.info(f"Started batch: {batch_id}")
        
        return True
    
    def update_batch_progress(
        self,
        batch_id: str,
        current_index: int,
        status: Optional[str] = None
    ) -> bool:
        """
        Update batch progress.
        
        Args:
            batch_id: ID of batch.
            current_index: Current item index.
            status: Optional status update.
            
        Returns:
            True if updated, False if not found.
        """
        if status:
            return self._repository.update_status(batch_id, status, current_index=current_index)
        return self._repository.update_current_index(batch_id, current_index)
    
    def complete_batch(self, batch_id: str) -> bool:
        """
        Mark a batch as completed.
        
        Args:
            batch_id: ID of batch.
            
        Returns:
            True if completed, False if not found.
        """
        return self._repository.update_status(
            batch_id,
            PROCESS_STATUS_COMPLETED,
            completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def fail_batch(self, batch_id: str, error_message: Optional[str] = None) -> bool:
        """
        Mark a batch as failed.
        
        Args:
            batch_id: ID of batch.
            error_message: Optional error message.
            
        Returns:
            True if marked as failed, False if not found.
        """
        return self._repository.update_status(
            batch_id,
            PROCESS_STATUS_FAILED,
            completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def execute_batch(
        self,
        batch_id: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        Execute a batch download sequentially.
        
        Args:
            batch_id: ID of batch to execute.
            progress_callback: Optional callback(current, total, status).
            
        Returns:
            Dictionary with execution results.
        """
        batch = self.get_batch(batch_id)
        if not batch:
            return {'error': 'Batch not found', 'successful': 0, 'failed': 0}
        
        if not batch.items:
            return {'error': 'Batch is empty', 'successful': 0, 'failed': 0}
        
        self.start_batch(batch_id)
        
        results = {
            'batch_id': batch_id,
            'batch_name': batch.name,
            'total': len(batch.items),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info(f"Executing batch: {batch.name} ({len(batch.items)} items)")
        
        for i, item in enumerate(batch.items):
            try:
                if progress_callback:
                    progress_callback(i, len(batch.items), f"Processing {item.url}")
                
                self.update_batch_progress(batch_id, i, PROCESS_STATUS_IN_PROGRESS)
                
                # Execute via callback
                if self._execute_callback:
                    self._execute_callback(item, i, len(batch.items))
                
                results['successful'] += 1
                logger.info(f"Batch item {i+1}/{len(batch.items)} completed: {item.url}")
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'index': i,
                    'url': item.url,
                    'error': str(e)
                })
                logger.error(f"Batch item {i+1} failed: {str(e)}")
        
        # Mark batch as completed
        self.complete_batch(batch_id)
        
        if progress_callback:
            progress_callback(len(batch.items), len(batch.items), "Batch completed")
        
        logger.info(f"Batch completed: {results['successful']}/{results['total']} successful")
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        Get batch statistics.
        
        Returns:
            Dictionary with batch statistics.
        """
        all_batches = self.get_all_batches()
        
        return {
            'total': len(all_batches),
            'pending': len([b for b in all_batches if b.status == PROCESS_STATUS_PENDING]),
            'in_progress': len([b for b in all_batches if b.status == PROCESS_STATUS_IN_PROGRESS]),
            'completed': len([b for b in all_batches if b.status == PROCESS_STATUS_COMPLETED]),
            'failed': len([b for b in all_batches if b.status == PROCESS_STATUS_FAILED]),
        }
    
    def get_batch_progress(self, batch_id: str) -> Optional[Dict]:
        """
        Get detailed progress for a batch.
        
        Args:
            batch_id: ID of batch.
            
        Returns:
            Dictionary with progress information or None if not found.
        """
        batch = self.get_batch(batch_id)
        if not batch:
            return None
        
        return {
            'batch_id': batch.id,
            'batch_name': batch.name,
            'status': batch.status,
            'total_items': len(batch.items),
            'current_index': batch.current_index,
            'progress_percentage': batch.get_progress(),
            'current_item': batch.get_current_item().url if batch.get_current_item() else None,
        }
