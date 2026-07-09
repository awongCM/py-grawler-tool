"""Read-side search API over the crawl index."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from grawlerx.storage import SearchResult, init_db, page_count, search_pages


class SearchService:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = db_path
        init_db(db_path)

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
