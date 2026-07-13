"""Minimal HTTP API for querying the crawl index."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, Query

from grawlerx.search_service import SearchService

app = FastAPI(title="Grawlerx Search API", version="0.1.0")


@lru_cache(maxsize=1)
def get_search_service() -> SearchService:
    return SearchService()


@app.get("/health")
def health():
    service = get_search_service()
    return {"status": "ok", **service.stats()}


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    service = get_search_service()
    results = service.search(q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }
