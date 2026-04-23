"""
History Repository for Download Records.

SQLite-based repository for managing download history with
full CRUD operations and query capabilities.
"""

from datetime import datetime
from typing import List, Optional

from dml_stream.exceptions.storage import RepositoryError
from dml_stream.storage.database import Database


class HistoryRecord:
    """Data class for history records."""

    def __init__(
        self,
        id: int,
        title: str,
        url: str,
        file_path: str,
        file_size: int,
        download_date: str,
        download_type: str,
        status: str,
        duration: Optional[int] = None,
        format: Optional[str] = None,
    ) -> None:
        self.id = id
        self.title = title
        self.url = url
        self.file_path = file_path
        self.file_size = file_size
        self.download_date = download_date
        self.download_type = download_type
        self.status = status
        self.duration = duration
        self.format = format

    @classmethod
    def from_row(cls, row) -> "HistoryRecord":
        """Create HistoryRecord from database row."""
        return cls(
            id=row["id"],
            title=row["title"],
            url=row["url"],
            file_path=row["file_path"],
            file_size=row["file_size"],
            download_date=row["download_date"],
            download_type=row["download_type"],
            status=row["status"],
            duration=row["duration"],
            format=row["format"],
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "download_date": self.download_date,
            "download_type": self.download_type,
            "status": self.status,
            "duration": self.duration,
            "format": self.format,
        }


class HistoryRepository:
    """
    Repository for download history persistence.
    
    Provides CRUD operations for download history records
    with support for searching, filtering, and statistics.
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize history repository.
        
        Args:
            db: Database connection manager.
        """
        self.db = db

    def add(
        self,
        title: str,
        url: str,
        file_path: str,
        file_size: int,
        download_type: str = "video",
        status: str = "success",
        duration: Optional[int] = None,
        format: Optional[str] = None,
    ) -> HistoryRecord:
        """
        Add a new download history record.
        
        Args:
            title: Title of downloaded content.
            url: Original YouTube URL.
            file_path: Path to downloaded file.
            file_size: File size in bytes.
            download_type: Type of download ('video', 'audio', 'playlist').
            status: Download status ('success', 'failed').
            duration: Video duration in seconds.
            format: Output format (e.g., 'mp4', 'mp3').
            
        Returns:
            Created HistoryRecord.
            
        Raises:
            RepositoryError: If insert fails.
        """
        download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with self.db as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO history (
                        title, url, file_path, file_size,
                        download_date, download_type, status, duration, format
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        title, url, file_path, file_size,
                        download_date, download_type, status, duration, format,
                    ),
                )
                record_id = cursor.lastrowid
                conn.commit()
            
            return HistoryRecord(
                id=record_id,
                title=title,
                url=url,
                file_path=file_path,
                file_size=file_size,
                download_date=download_date,
                download_type=download_type,
                status=status,
                duration=duration,
                format=format,
            )
        except Exception as e:
            raise RepositoryError(f"Failed to add history record: {e}", "history")

    def get_all(self, limit: Optional[int] = None) -> List[HistoryRecord]:
        """
        Get all history records.
        
        Args:
            limit: Optional maximum number of records to return.
            
        Returns:
            List of HistoryRecord objects.
        """
        try:
            with self.db as conn:
                query = "SELECT * FROM history ORDER BY download_date DESC"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                rows = cursor.fetchall()
                return [HistoryRecord.from_row(row) for row in rows]
        except Exception as e:
            raise RepositoryError(f"Failed to get history records: {e}", "history")

    def get_by_id(self, record_id: int) -> Optional[HistoryRecord]:
        """Get a history record by ID."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "SELECT * FROM history WHERE id = ?", (record_id,)
                )
                row = cursor.fetchone()
                return HistoryRecord.from_row(row) if row else None
        except Exception as e:
            raise RepositoryError(f"Failed to get history record: {e}", "history")

    def get_by_url(self, url: str) -> List[HistoryRecord]:
        """Get history records by URL."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "SELECT * FROM history WHERE url = ? ORDER BY download_date DESC",
                    (url,),
                )
                rows = cursor.fetchall()
                return [HistoryRecord.from_row(row) for row in rows]
        except Exception as e:
            raise RepositoryError(f"Failed to get history by URL: {e}", "history")

    def get_by_type(self, download_type: str) -> List[HistoryRecord]:
        """Get history records by download type."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "SELECT * FROM history WHERE download_type = ? ORDER BY download_date DESC",
                    (download_type,),
                )
                rows = cursor.fetchall()
                return [HistoryRecord.from_row(row) for row in rows]
        except Exception as e:
            raise RepositoryError(f"Failed to get history by type: {e}", "history")

    def get_by_status(self, status: str) -> List[HistoryRecord]:
        """Get history records by status."""
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "SELECT * FROM history WHERE status = ? ORDER BY download_date DESC",
                    (status,),
                )
                rows = cursor.fetchall()
                return [HistoryRecord.from_row(row) for row in rows]
        except Exception as e:
            raise RepositoryError(f"Failed to get history by status: {e}", "history")

    def get_recent(self, limit: int = 10) -> List[HistoryRecord]:
        """Get most recent downloads."""
        return self.get_all(limit=limit)

    def get_failed(self) -> List[HistoryRecord]:
        """Get all failed downloads."""
        return self.get_by_status("failed")

    def search(self, query: str) -> List[HistoryRecord]:
        """
        Search history by title or URL.
        
        Args:
            query: Search query string.
            
        Returns:
            List of matching HistoryRecord objects.
        """
        try:
            with self.db as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM history
                    WHERE title LIKE ? OR url LIKE ?
                    ORDER BY download_date DESC
                    """,
                    (f"%{query}%", f"%{query}%"),
                )
                rows = cursor.fetchall()
                return [HistoryRecord.from_row(row) for row in rows]
        except Exception as e:
            raise RepositoryError(f"Failed to search history: {e}", "history")

    def delete(self, record_id: int) -> bool:
        """
        Delete a history record.
        
        Args:
            record_id: ID of record to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        try:
            with self.db as conn:
                cursor = conn.execute(
                    "DELETE FROM history WHERE id = ?", (record_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise RepositoryError(f"Failed to delete history record: {e}", "history")

    def clear(self) -> int:
        """
        Clear all history records.
        
        Returns:
            Number of records deleted.
        """
        try:
            with self.db as conn:
                cursor = conn.execute("DELETE FROM history")
                count = cursor.rowcount
                conn.commit()
                return count
        except Exception as e:
            raise RepositoryError(f"Failed to clear history: {e}", "history")

    def count(self) -> int:
        """Get total number of history records."""
        try:
            with self.db as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM history")
                return cursor.fetchone()[0]
        except Exception as e:
            raise RepositoryError(f"Failed to count history records: {e}", "history")

    def get_stats(self) -> dict:
        """
        Get download statistics.
        
        Returns:
            Dictionary with statistics (total, by_type, by_status, total_size).
        """
        try:
            with self.db as conn:
                # Total count
                cursor = conn.execute("SELECT COUNT(*) FROM history")
                total = cursor.fetchone()[0]
                
                # Count by type
                cursor = conn.execute(
                    "SELECT download_type, COUNT(*) FROM history GROUP BY download_type"
                )
                by_type = {row["download_type"]: row["COUNT(*)"] for row in cursor.fetchall()}
                
                # Count by status
                cursor = conn.execute(
                    "SELECT status, COUNT(*) FROM history GROUP BY status"
                )
                by_status = {row["status"]: row["COUNT(*)"] for row in cursor.fetchall()}
                
                # Total size
                cursor = conn.execute("SELECT SUM(file_size) FROM history WHERE status = 'success'")
                total_size = cursor.fetchone()[0] or 0
                
                return {
                    "total": total,
                    "by_type": by_type,
                    "by_status": by_status,
                    "total_size": total_size,
                }
        except Exception as e:
            raise RepositoryError(f"Failed to get stats: {e}", "history")
