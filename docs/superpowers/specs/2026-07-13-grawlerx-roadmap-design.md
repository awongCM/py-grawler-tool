# Grawlerx Roadmap Design Spec

**Date:** 2026-07-13  
**Status:** Draft — ready for review  
**Scope:** Post-Phase-1 roadmap for `py-grawler-tool`

---

## Context

Phase 1 delivered the crawl/search **internals**:

- Keyword-aware Scrapy crawler
- SQLite FTS5 index + storage pipeline
- CLI and FastAPI search API (`/search`, `/health`)

The original README listed three goals. Items 1–2 are done. Item 3 — a Google-like frontend — and several quality-of-life improvements remain.

This document defines phased work that stays true to the repo's purpose: **learning how search engines work**, not competing with production systems.

---

## Phase Summary

| Phase | Name | Status | Outcome |
|-------|------|--------|---------|
| 1 | Crawl + Index + Search API | **Complete** | End-to-end keyword crawl, FTS index, CLI/API search |
| 2 | Search Frontend | **Next** | Browser UI over existing API; completes original README vision |
| 3 | Crawl Quality & Control | Planned | Safer, more predictable crawls and better ranking |
| 4 | Local Ops & Packaging | Planned | One-command dev workflow and optional Render deploy |

Phases are sequential. Each phase ships independently testable software.

---

## Phase 1 (Complete) — Reference

**Goal:** Prove crawl → index → search works locally.

**Components:**

```
Seed URLs → SearchCrawler → StoragePipeline → SQLite/FTS5 → SearchService → CLI / FastAPI
```

**Delivered:**

- `keyword_search.py` — scoring, link heuristics, FTS query builder
- `storage.py` — SQLite schema, FTS5 triggers, WAL concurrency
- `search_crawler.py` — keyword crawl with depth control
- `api.py` + `__main__.py` — HTTP and CLI interfaces
- 13 tests

**Explicit non-goals (unchanged):** distributed crawling, production ranking, public multi-tenant deployment.

---

## Phase 2 — Search Frontend

### Goal

Add a minimal browser UI that queries the existing `/search` API and displays results in a Google-inspired layout. Completes README item 3 without introducing a separate frontend framework.

### User stories

1. As a learner, I open `http://127.0.0.1:8000/` and see a search box centered on the page.
2. I type a query, submit, and land on `/search?q=...` with a list of results (title link, snippet, URL).
3. Empty or failed searches show a clear message, not a broken page.
4. The UI works with zero extra build steps — `python -m grawlerx serve` is enough.

### Architecture

```
Browser
  ├─ GET /              → static index.html (search box)
  └─ GET /search?q=...  → server-rendered HTML results page
                              └─ SearchService.search(q)  (same as JSON API)
```

**Approach:** Server-rendered HTML via FastAPI + Jinja2 templates. One small CSS file. No React/Vue build chain.

**Why server-rendered (recommended):**

| Option | Pros | Cons |
|--------|------|------|
| **A. Server-rendered HTML (recommended)** | No build step; easy to test; matches learning focus | Less "SPA-like" interactivity |
| B. Static SPA + fetch API | Closer to modern apps | Adds build/bundling overhead for little gain here |
| C. HTMX | Nice progressive enhancement | Extra dependency for a two-page UI |

### Components

| File | Responsibility |
|------|----------------|
| `grawlerx/templates/base.html` | Shared layout, CSS link, footer |
| `grawlerx/templates/index.html` | Landing search form |
| `grawlerx/templates/results.html` | Results list |
| `grawlerx/static/style.css` | Minimal Google-inspired styling |
| `grawlerx/api.py` | Mount static files; add HTML routes alongside JSON API |

### API contract (unchanged JSON + new HTML)

- `GET /search?q=...` — keep existing JSON response for programmatic use
- `GET /results?q=...` — new HTML results page (avoids content-negotiation complexity on `/search`)
- `GET /` — landing page

### UI requirements

- **Landing:** centered logo text ("Grawlerx"), single search input, submit button
- **Results:** query echoed at top; each result shows title (linked), snippet, green URL line
- **Empty state:** "No results for …" with link back to home
- **Error state:** invalid/blank query redirects to `/` or shows inline message

### Testing

- FastAPI TestClient tests for `/`, `/results?q=cattle`, empty query
- Assert HTML contains result titles from seeded test DB
- Existing JSON `/search` tests remain unchanged

### Out of scope for Phase 2

- Pagination beyond `limit` param
- Autocomplete / typeahead
- Crawl management UI
- Authentication

---

## Phase 3 — Crawl Quality & Control

### Goal

Make crawls more predictable and search results more useful, without changing the storage engine.

### Features

1. **`allowed_domains` spider argument** — comma-separated list; link following restricted to those domains (seeds may be outside list but external links won't be followed)
2. **Stem-aware keyword matching** — optional simple suffix stripping (`cows` → `cow`) for scoring and link heuristics
3. **Sitemap seed loader** — `python -m grawlerx seeds --sitemap URL` writes candidate URLs filtered by keywords
4. **Recrawl metadata** — store `last_crawled_at`, skip unchanged pages when `ETag`/`Last-Modified` match (best-effort)
5. **Rank blending** — combine FTS `bm25` rank with `relevance_score` for final result ordering

### Architecture additions

```
Sitemap URL → seed_loader.py → urls.txt
SearchCrawler(allowed_domains=...) → filtered link graph
search_pages() → blended rank (bm25 + relevance_score)
```

### Out of scope

- Distributed crawl queue
- JavaScript rendering (Playwright/Splash)
- NLP embeddings / vector search

---

## Phase 4 — Local Ops & Packaging

### Goal

Reduce friction running the full stack locally; optionally deploy the search API as a Render web service.

### Features

1. **`docker-compose.yml`** (optional) — one service for API; volume mount for `data/`
2. **`Makefile` or documented scripts** — `make crawl`, `make serve`, `make test`
3. **Render Blueprint snippet** — web service binding `0.0.0.0:$PORT`, `GRAWLERX_DB_PATH` on persistent disk (Render disk required for SQLite across restarts)
4. **README "Full demo" section** — crawl → search in browser in 5 commands

### Render constraints (from platform rules)

- Bind to `0.0.0.0:$PORT`
- SQLite on ephemeral filesystem is lost on restart — attach a Render disk or document that index is ephemeral on free tier
- One web service per Blueprint entry (API serves static + JSON)

### Out of scope

- Managed Postgres migration (SQLite is fine for learning scale)
- Separate worker service for crawling (crawl remains CLI-triggered)

---

## Cross-cutting decisions

### Data store

Stay on **SQLite FTS5** through Phase 3. Sufficient for thousands of pages and keeps the learning focus on crawl/index/search mechanics.

### Dependencies

- Phase 2 adds: `jinja2` (FastAPI template support)
- Phase 3 adds: none required (stdlib + existing deps)
- Phase 4 adds: optional `docker` only

### Success criteria by phase

| Phase | Done when |
|-------|-----------|
| 2 | User can search in browser; tests pass; README updated |
| 3 | Domain-restricted crawl works; blended ranking tested; sitemap seed CLI works |
| 4 | Documented one-command demo; Render blueprint validates |

---

## Recommended execution order

1. **Phase 2** — highest value; completes original README
2. **Phase 3** — improves crawl trustworthiness before any public deploy
3. **Phase 4** — polish once UI and crawl behavior are stable

---

## Open questions (deferred)

- **Branding:** keep "Grawlerx" placeholder or rename? Default: keep.
- **Frontend framework:** only revisit if Phase 2 UI needs interactivity (filters, pagination). Default: stay server-rendered.
- **Database migration:** only if index exceeds ~50k pages or concurrent write load grows. Default: stay SQLite.

---

## References

- `README.md` — current usage
- `grawlerx/grawlerx/api.py` — existing search API
- Original README TODO items 1–3
