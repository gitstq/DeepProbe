"""
Local storage engine using SQLite.
本地SQLite存储引擎。
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class StorageEngine:
    """SQLite-based local storage for research data."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self._db_path = Path(db_path)
        else:
            self._db_dir = Path(os.path.expanduser("~/.deepprobe"))
            self._db_dir.mkdir(parents=True, exist_ok=True)
            self._db_path = self._db_dir / "deepprobe.db"

        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self) -> None:
        """Initialize database tables."""
        cursor = self._conn.cursor()

        # Research sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                depth TEXT DEFAULT 'standard',
                status TEXT DEFAULT 'pending',
                sources TEXT DEFAULT '[]',
                total_results INTEGER DEFAULT 0,
                analysis TEXT,
                report_format TEXT DEFAULT 'markdown',
                created_at TEXT NOT NULL,
                completed_at TEXT,
                metadata TEXT DEFAULT '{}'
            )
        """)

        # Search results cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                source TEXT NOT NULL,
                title TEXT,
                url TEXT,
                snippet TEXT,
                relevance_score REAL DEFAULT 0.0,
                fetched_at TEXT NOT NULL,
                expires_at TEXT,
                UNIQUE(query, source, url)
            )
        """)

        # Export history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                research_id TEXT NOT NULL,
                format TEXT NOT NULL,
                file_path TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (research_id) REFERENCES research(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_query ON research(query)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_created ON research(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_query ON search_cache(query)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON search_cache(expires_at)")

        self._conn.commit()

    def save_research(
        self,
        research_id: str,
        query: str,
        depth: str,
        sources: List[str],
        total_results: int,
        analysis: Dict[str, Any],
        status: str = "completed",
    ) -> None:
        """Save or update a research session."""
        cursor = self._conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO research
            (id, query, depth, status, sources, total_results, analysis, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            research_id,
            query,
            depth,
            status,
            json.dumps(sources),
            total_results,
            json.dumps(analysis, ensure_ascii=False),
            now,
            now if status == "completed" else None,
        ))

        self._conn.commit()

    def get_research(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Get a research session by ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM research WHERE id = ?", (research_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["sources"] = json.loads(data["sources"])
            data["analysis"] = json.loads(data["analysis"]) if data["analysis"] else {}
            data["metadata"] = json.loads(data["metadata"])
            return data
        return None

    def search_research(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search research history by keyword."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM research
            WHERE query LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f"%{keyword}%", limit))

        results = []
        for row in cursor.fetchall():
            data = dict(row)
            data["sources"] = json.loads(data["sources"])
            data["analysis"] = json.loads(data["analysis"]) if data["analysis"] else {}
            results.append(data)
        return results

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent research history."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT id, query, depth, status, sources, total_results, created_at, completed_at
            FROM research
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cursor.fetchall():
            data = dict(row)
            data["sources"] = json.loads(data["sources"])
            results.append(data)
        return results

    def cache_results(
        self,
        query: str,
        source: str,
        results: List[Dict[str, Any]],
        ttl_hours: int = 24,
    ) -> None:
        """Cache search results."""
        cursor = self._conn.cursor()
        now = datetime.now()

        for result in results:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO search_cache
                    (query, source, title, url, snippet, relevance_score, fetched_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    query,
                    source,
                    result.get("title", ""),
                    result.get("url", ""),
                    result.get("snippet", ""),
                    result.get("relevance_score", 0.0),
                    now.isoformat(),
                    (now + __import__("datetime").timedelta(hours=ttl_hours)).isoformat(),
                ))
            except Exception:
                continue

        self._conn.commit()

    def get_cached_results(self, query: str, source: str) -> List[Dict[str, Any]]:
        """Get cached search results if not expired."""
        cursor = self._conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
            SELECT title, url, snippet, relevance_score, source
            FROM search_cache
            WHERE query = ? AND source = ? AND expires_at > ?
            ORDER BY relevance_score DESC
        """, (query, source, now))

        return [dict(row) for row in cursor.fetchall()]

    def clear_expired_cache(self) -> int:
        """Clear expired cache entries. Returns count of cleared entries."""
        cursor = self._conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("DELETE FROM search_cache WHERE expires_at <= ?", (now,))
        deleted = cursor.rowcount
        self._conn.commit()
        return deleted

    def delete_research(self, research_id: str) -> bool:
        """Delete a research session."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM research WHERE id = ?", (research_id,))
        cursor.execute("DELETE FROM exports WHERE research_id = ?", (research_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
