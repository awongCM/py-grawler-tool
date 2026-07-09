"""Minimal HTTP API for querying the crawl index."""

from __future__ import annotations

from fastapi import FastAPI, Query

from grawlerx.search_service import SearchService

app = FastAPI(title="Grawlerx Search API", version="0.1.0")
search_service = SearchService()


@app.get("/health")
def health():
    return {"status": "ok", **search_service.stats()}


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    results = search_service.search(q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }
