"""Read-side search API over the crawl index."""

from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from grawlerx.storage import DEFAULT_DB_PATH, SearchResult, init_db, page_count, search_pages


def resolve_db_path(db_path: Path | str | None = None) -> Path | str:
    if db_path is not None:
        return db_path
    return os.environ.get("GRAWLERX_DB_PATH", str(DEFAULT_DB_PATH))


class SearchService:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = resolve_db_path(db_path)
        init_db(self.db_path)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        results = search_pages(query, limit=limit, db_path=self.db_path)
        return [self._serialize(result) for result in results]

    def stats(self) -> dict[str, int]:
        return {"indexed_pages": page_count(self.db_path)}

    @staticmethod
    def _serialize(result: SearchResult) -> dict:
        payload = asdict(result)
        payload["snippet"] = result.description or result.title
        return payload
