"""
Queue Repository for Download Queue Management.

SQLite-based repository for managing download queue with
support for prioritization and status tracking.
"""

from datetime import datetime
from typing import List, Optional

from dml_stream.exceptions.storage import RepositoryError
from dml_stream.storage.database import Database


class QueueRecord:
    """Data class for queue records."""

    def __init__(
        self,
        id: int,
        url: str,
        download_type: str,
        output_folder: str,
        priority: int,
        status: str,
        created_at: str,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ) -> None:
        self.id = id
        self.url = url
        self.download_type = download_type
        self.output_folder = output_folder
        self.priority = priority
        self.status = status
        self.created_at = created_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.error_message = error_message
        self.retry_count = retry_count
        self.max_retries = max_retries

    @classmethod
    def from_row(cls, row) -> "QueueRecord":
        """Create QueueRecord from database row."""
        return cls(
            id=row["id"],
            url=row["url"],
            download_type=row["download_type"],
            output_folder=row["output_folder"],
            priority=row["priority"],
            status=row["status"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            error_message=row["error_message"],
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "download_type": self.download_type,
            "output_folder": self.output_folder,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }

    def can_retry(self) -> bool:
        """Check if this record can be retried."""
        return self.retry_count < self.max_retries


class QueueRepository:
    """
    Repository for download queue persistence.
    
    Provides CRUD operations for download queue with
    support for prioritization, retries, and status tracking.
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize queue repository.
        
        Args:
            db: Database connection manager.
        """
        self.db = db

    def add(
        self,
        url: str,
        download_type: str,
        output_folder: str,
        priority: int = 0,
        max_retries: int = 3,
    ) -> QueueRecord:
        """
        Add a new item to the download queue.
        
        Args:
            url: YouTube URL to download.
            download_type: Type of download ('video', 'audio', 'playlist').
            output_folder: Destination folder.
            priority: Priority level (higher = more urgent).
            max_retries: Maximum retry attempts.
            
        Returns:
            Created QueueRecord.
        """
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with self.db as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO download_queue (
                        url, download_type, output_folder, priority,
                        status, created_at, max_retries
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        url, download_type, output_folder, priority,
                        "pending", created_at, max_retries,
                    ),
                )
                record_id = cursor.lastrowid
                conn.commit()
            
            return QueueRecord(
                id=record_id,
                url=url,
                download_type=download_type,
                output_folder=output_folder,
                priority=priority,
                status="pending",
                created_at=created_at,
                max_retries=max_retries,
            )
        except Exception as e:
            raise RepositoryError(f"Failed to add to queue: {e}", "queue")

    def get_all(self) -> List[QueueRecord]:
        """Get all queue records ordered by priority and creation date."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM download_queue
                    ORDER BY priority DESC, created_at ASC
                    """
                )
                rows = cursor.fetchall()
                return [QueueRecord.from_row(row) for row in rows]
        except Exception as e:
            raise RepositoryError(f"Failed to get queue records: {e}", "queue")

    def get_by_id(self, record_id: int) -> Optional[QueueRecord]:
        """Get a queue record by ID."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "SELECT * FROM download_queue WHERE id = ?", (record_id,)
                )
                row = cursor.fetchone()
                return QueueRecord.from_row(row) if row else None
        except Exception as e:
            raise RepositoryError(f"Failed to get queue record: {e}", "queue")

    def get_by_status(self, status: str) -> List[QueueRecord]:
        """Get queue records by status."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM download_queue
                    WHERE status = ?
                    ORDER BY priority DESC, created_at ASC
                    """,
                    (status,),
                )
                rows = cursor.fetchall()
                return [QueueRecord.from_row(row) for row in rows]
        except Exception as e:
            raise RepositoryError(f"Failed to get queue by status: {e}", "queue")

    def get_pending(self) -> List[QueueRecord]:
        """Get all pending queue items."""
        return self.get_by_status("pending")

    def get_running(self) -> List[QueueRecord]:
        """Get all running queue items."""
        return self.get_by_status("running")

    def get_next(self) -> Optional[QueueRecord]:
        """
        Get the next pending item (highest priority, oldest first).
        
        Returns:
            Next QueueRecord or None if queue is empty.
        """
        try:
            with self.db as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM download_queue
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()
                return QueueRecord.from_row(row) if row else None
        except Exception as e:
            raise RepositoryError(f"Failed to get next queue item: {e}", "queue")

    def update_status(
        self,
        record_id: int,
        status: str,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Update status of a queue item.
        
        Args:
            record_id: ID of record to update.
            status: New status ('pending', 'running', 'completed', 'failed').
            error_message: Optional error message for failed status.
            
        Returns:
            True if updated successfully.
        """
        try:
            with self.db as conn:
                updates = ["status = ?"]
                params: list = [status]
                
                if status == "running":
                    updates.append("started_at = ?")
                    params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                elif status == "completed":
                    updates.append("completed_at = ?")
                    params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                elif status == "failed" and error_message:
                    updates.append("error_message = ?")
                    params.append(error_message)
                    updates.append("retry_count = retry_count + 1")
                
                params.append(record_id)
                
                cursor = conn.execute(
                    f"UPDATE download_queue SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise RepositoryError(f"Failed to update queue status: {e}", "queue")

    def delete(self, record_id: int) -> bool:
        """Delete a queue item."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "DELETE FROM download_queue WHERE id = ?", (record_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise RepositoryError(f"Failed to delete queue record: {e}", "queue")

    def clear(self, status: Optional[str] = None) -> int:
        """
        Clear queue items.
        
        Args:
            status: Optional status filter (clear all if None).
            
        Returns:
            Number of records deleted.
        """
        try:
            with self.db as conn:
                if status:
                    cursor = conn.execute(
                        "DELETE FROM download_queue WHERE status = ?", (status,)
                    )
                else:
                    cursor = conn.execute("DELETE FROM download_queue")
                count = cursor.rowcount
                conn.commit()
                return count
        except Exception as e:
            raise RepositoryError(f"Failed to clear queue: {e}", "queue")

    def count(self, status: Optional[str] = None) -> int:
        """Get number of queue items, optionally filtered by status."""
        try:
            with self.db as conn:
                if status:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM download_queue WHERE status = ?",
                        (status,),
                    )
                else:
                    cursor = conn.execute("SELECT COUNT(*) FROM download_queue")
                return cursor.fetchone()[0]
        except Exception as e:
            raise RepositoryError(f"Failed to count queue items: {e}", "queue")

    def retry_failed(self) -> int:
        """
        Reset failed items to pending for retry.
        
        Returns:
            Number of items reset.
        """
        try:
            with self.db as conn:
                cursor = conn.execute(
                    """
                    UPDATE download_queue
                    SET status = 'pending', error_message = NULL
                    WHERE status = 'failed' AND retry_count < max_retries
                    """
                )
                count = cursor.rowcount
                conn.commit()
                return count
        except Exception as e:
            raise RepositoryError(f"Failed to retry failed items: {e}", "queue")
