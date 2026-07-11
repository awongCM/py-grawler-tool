"""SQLite persistence and FTS5 search index for crawled pages."""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from grawlerx.keyword_search import build_fts_query

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "grawlerx.db"
SQLITE_BUSY_RETRIES = 5
SQLITE_BUSY_BACKOFF_SECONDS = 0.05

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    description TEXT,
    body TEXT,
    relevance_score REAL NOT NULL DEFAULT 0,
    keywords TEXT,
    crawled_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
    title,
    description,
    body,
    content='pages',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
    INSERT INTO pages_fts(rowid, title, description, body)
    VALUES (new.id, new.title, new.description, new.body);
END;

CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages BEGIN
    INSERT INTO pages_fts(pages_fts, rowid, title, description, body)
    VALUES ('delete', old.id, old.title, old.description, old.body);
END;

CREATE TRIGGER IF NOT EXISTS pages_au AFTER UPDATE ON pages BEGIN
    INSERT INTO pages_fts(pages_fts, rowid, title, description, body)
    VALUES ('delete', old.id, old.title, old.description, old.body);
    INSERT INTO pages_fts(rowid, title, description, body)
    VALUES (new.id, new.title, new.description, new.body);
END;
"""


@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str
    description: str
    relevance_score: float
    rank: float


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=30000")
    return connection


def init_db(db_path: Path | str | None = None) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA)
        connection.commit()


def _run_with_retry(operation):
    for attempt in range(SQLITE_BUSY_RETRIES):
        try:
            return operation()
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower() or attempt == SQLITE_BUSY_RETRIES - 1:
                raise
            time.sleep(SQLITE_BUSY_BACKOFF_SECONDS * (attempt + 1))


def upsert_page(
    *,
    url: str,
    title: str = "",
    description: str = "",
    body: str = "",
    relevance_score: float = 0.0,
    keywords: str = "",
    db_path: Path | str | None = None,
) -> None:
    crawled_at = datetime.now(timezone.utc).isoformat()

    def _write() -> None:
        with connect(db_path) as connection:
            connection.execute(
                """
                INSERT INTO pages (url, title, description, body, relevance_score, keywords, crawled_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    body=excluded.body,
                    relevance_score=excluded.relevance_score,
                    keywords=excluded.keywords,
                    crawled_at=excluded.crawled_at
                """,
                (url, title, description, body, relevance_score, keywords, crawled_at),
            )
            connection.commit()

    _run_with_retry(_write)


def search_pages(
    query: str,
    *,
    limit: int = 20,
    db_path: Path | str | None = None,
) -> list[SearchResult]:
    fts_query = build_fts_query(query)
    if not fts_query:
        return []

    try:
        with connect(db_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    p.url,
                    COALESCE(p.title, '') AS title,
                    COALESCE(p.description, '') AS description,
                    p.relevance_score,
                    bm25(pages_fts) AS rank
                FROM pages_fts
                JOIN pages AS p ON p.id = pages_fts.rowid
                WHERE pages_fts MATCH ?
                ORDER BY rank, p.relevance_score DESC
                LIMIT ?
                """,
                (fts_query, limit),
            ).fetchall()
    except sqlite3.OperationalError:
        return []

    return [
        SearchResult(
            url=row["url"],
            title=row["title"],
            description=row["description"],
            relevance_score=float(row["relevance_score"]),
            rank=float(row["rank"]),
        )
        for row in rows
    ]


def page_count(db_path: Path | str | None = None) -> int:
    with connect(db_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS count FROM pages").fetchone()
    return int(row["count"])
