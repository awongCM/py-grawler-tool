"""Minimal HTTP API and HTML frontend for querying the crawl index."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from grawlerx.search_service import SearchService

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"

app = FastAPI(title="Grawlerx Search API", version="0.2.0")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@lru_cache(maxsize=1)
def get_search_service() -> SearchService:
    return SearchService()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/results", response_class=HTMLResponse)
def results_html(
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
):
    service = get_search_service()
    results = service.search(q, limit=limit)
    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "query": q,
            "count": len(results),
            "results": results,
        },
    )


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
