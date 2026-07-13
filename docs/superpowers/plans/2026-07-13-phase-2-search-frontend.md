# Phase 2: Search Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal Google-inspired browser UI (landing page + results page) served by the existing FastAPI app, completing README item 3.

**Architecture:** FastAPI serves Jinja2 templates and a static CSS file. HTML results route (`/results`) calls the same `SearchService` as the JSON `/search` endpoint. No frontend build chain.

**Tech Stack:** FastAPI, Jinja2, vanilla HTML/CSS, pytest + httpx TestClient

**Design spec:** `docs/superpowers/specs/2026-07-13-grawlerx-roadmap-design.md` (Phase 2 section)

---

## File map

| File | Action | Responsibility |
|------|--------|----------------|
| `grawlerx/requirements.txt` | Modify | Add `jinja2` |
| `grawlerx/grawlerx/api.py` | Modify | Templates, static mount, HTML routes |
| `grawlerx/grawlerx/templates/base.html` | Create | Shared layout |
| `grawlerx/grawlerx/templates/index.html` | Create | Landing search form |
| `grawlerx/grawlerx/templates/results.html` | Create | Results list |
| `grawlerx/grawlerx/static/style.css` | Create | Minimal styling |
| `grawlerx/tests/test_frontend.py` | Create | HTML route tests |
| `README.md` | Modify | Browser usage docs |

---

### Task 1: Add Jinja2 dependency

**Files:**
- Modify: `grawlerx/requirements.txt`

- [ ] **Step 1: Add jinja2 to requirements**

```text
jinja2>=3.1,<4
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r grawlerx/requirements.txt`  
Expected: Successful install with no errors

- [ ] **Step 3: Commit**

```bash
git add grawlerx/requirements.txt
git commit -m "chore: add jinja2 for search frontend templates"
```

---

### Task 2: Create templates and static assets

**Files:**
- Create: `grawlerx/grawlerx/templates/base.html`
- Create: `grawlerx/grawlerx/templates/index.html`
- Create: `grawlerx/grawlerx/templates/results.html`
- Create: `grawlerx/grawlerx/static/style.css`

- [ ] **Step 1: Create base template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Grawlerx{% endblock %}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body class="{% block body_class %}{% endblock %}">
  {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Create index template**

```html
{% extends "base.html" %}

{% block title %}Grawlerx{% endblock %}
{% block body_class %}landing{% endblock %}

{% block content %}
<main class="landing-main">
  <h1 class="logo">Grawlerx</h1>
  <form class="search-form" action="/results" method="get">
    <input
      type="search"
      name="q"
      class="search-input"
      placeholder="Search the crawl index"
      autofocus
      required
    >
    <div class="search-actions">
      <button type="submit">Search</button>
    </div>
  </form>
</main>
{% endblock %}
```

- [ ] **Step 3: Create results template**

```html
{% extends "base.html" %}

{% block title %}{{ query }} - Grawlerx{% endblock %}
{% block body_class %}results{% endblock %}

{% block content %}
<header class="results-header">
  <a href="/" class="logo-small">Grawlerx</a>
  <form class="search-form compact" action="/results" method="get">
    <input type="search" name="q" class="search-input" value="{{ query }}" required>
    <button type="submit">Search</button>
  </form>
</header>

<main class="results-main">
  <p class="results-meta">About {{ count }} result{% if count != 1 %}s{% endif %}</p>

  {% if results %}
    <ul class="results-list">
      {% for result in results %}
        <li class="result-item">
          <a class="result-title" href="{{ result.url }}">{{ result.title or result.url }}</a>
          <p class="result-url">{{ result.url }}</p>
          <p class="result-snippet">{{ result.snippet }}</p>
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p class="empty-state">No results for <strong>{{ query }}</strong>. <a href="/">Try another search</a>.</p>
  {% endif %}
</main>
{% endblock %}
```

- [ ] **Step 4: Create stylesheet**

```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: #202124;
  background: #fff;
}

a {
  color: #1a0dab;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.landing-main {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.logo {
  font-size: 64px;
  font-weight: 400;
  margin: 0 0 24px;
  letter-spacing: -2px;
}

.search-form {
  width: min(584px, 100%);
}

.search-form.compact {
  flex: 1;
  display: flex;
  gap: 8px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #dfe1e5;
  border-radius: 24px;
  font-size: 16px;
}

.search-input:focus {
  outline: none;
  box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
  border-color: transparent;
}

.search-actions {
  margin-top: 24px;
  text-align: center;
}

.search-actions button,
.search-form.compact button {
  background: #f8f9fa;
  border: 1px solid #f8f9fa;
  border-radius: 4px;
  color: #3c4043;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}

.results-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px 24px;
  border-bottom: 1px solid #ebebeb;
}

.logo-small {
  font-size: 20px;
  color: #202124;
  font-weight: 500;
}

.results-main {
  max-width: 650px;
  padding: 12px 24px 48px 180px;
}

.results-meta {
  color: #70757a;
  font-size: 14px;
}

.results-list {
  list-style: none;
  padding: 0;
  margin: 16px 0 0;
}

.result-item {
  margin-bottom: 24px;
}

.result-title {
  font-size: 20px;
  line-height: 1.3;
}

.result-url {
  color: #006621;
  font-size: 14px;
  margin: 4px 0;
  word-break: break-all;
}

.result-snippet {
  color: #4d5156;
  font-size: 14px;
  line-height: 1.58;
  margin: 0;
}

.empty-state {
  margin-top: 24px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .results-main {
    padding-left: 24px;
  }

  .results-header {
    flex-direction: column;
    align-items: stretch;
  }
}
```

- [ ] **Step 5: Commit**

```bash
git add grawlerx/grawlerx/templates/ grawlerx/grawlerx/static/
git commit -m "feat: add search frontend templates and styles"
```

---

### Task 3: Wire HTML routes into FastAPI

**Files:**
- Modify: `grawlerx/grawlerx/api.py`

- [ ] **Step 1: Write failing frontend test**

Create `grawlerx/tests/test_frontend.py`:

```python
import pytest
from fastapi.testclient import TestClient

from grawlerx.api import app, get_search_service
from grawlerx.storage import init_db, upsert_page


def test_landing_page_renders_search_form():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Grawlerx" in response.text
    assert 'name="q"' in response.text


def test_results_page_renders_matches(tmp_path, monkeypatch):
    db_path = tmp_path / "frontend.db"
    monkeypatch.setenv("GRAWLERX_DB_PATH", str(db_path))
    init_db(db_path)
    upsert_page(
        url="https://example.com/cattle",
        title="Cattle page",
        description="All about cattle",
        body="Cattle facts",
        relevance_score=0.9,
        keywords="cattle",
        db_path=db_path,
    )

    get_search_service.cache_clear()
    client = TestClient(app)

    response = client.get("/results", params={"q": "cattle"})
    assert response.status_code == 200
    assert "Cattle page" in response.text
    assert "https://example.com/cattle" in response.text

    get_search_service.cache_clear()


def test_results_page_shows_empty_state(tmp_path, monkeypatch):
    db_path = tmp_path / "empty.db"
    monkeypatch.setenv("GRAWLERX_DB_PATH", str(db_path))
    init_db(db_path)

    get_search_service.cache_clear()
    client = TestClient(app)

    response = client.get("/results", params={"q": "zzznomatch"})
    assert response.status_code == 200
    assert "No results" in response.text

    get_search_service.cache_clear()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd grawlerx && PYTHONPATH=. pytest tests/test_frontend.py -v`  
Expected: FAIL — `/` or `/results` return 404

- [ ] **Step 3: Update api.py**

Replace `grawlerx/grawlerx/api.py` with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd grawlerx && PYTHONPATH=. pytest tests/test_frontend.py tests/test_api.py -v`  
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add grawlerx/grawlerx/api.py grawlerx/tests/test_frontend.py
git commit -m "feat: add HTML search frontend routes"
```

---

### Task 4: Update README and verify full demo

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add browser search section to README**

Insert after the HTTP API section:

```markdown
## Search in the browser

```bash
python -m grawlerx serve
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/), search, and view results at `/results?q=...`.

The JSON API remains available at `/search?q=...` for programmatic use.
```

- [ ] **Step 2: Run full test suite**

Run: `cd grawlerx && PYTHONPATH=. pytest -q`  
Expected: All tests PASS (16+ total)

- [ ] **Step 3: Manual smoke test**

Run:

```bash
cd grawlerx
python -m grawlerx crawl --keywords "cattle,cow" --max-depth 0
python -m grawlerx serve
```

Open `http://127.0.0.1:8000/`, search for `cattle`, confirm results render.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: document browser search UI"
```

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| Landing page with search box | Task 2, Task 3 |
| Results page with title/snippet/URL | Task 2, Task 3 |
| Empty state | Task 2 (`results.html`), Task 3 test |
| No build step | Task 1–3 (server-rendered only) |
| JSON API unchanged | Task 3 (`/search` preserved) |
| Tests | Task 3 (`test_frontend.py`) |
| README update | Task 4 |

## Post-Phase-2 handoff

After Phase 2 merges, begin Phase 3 (Crawl Quality & Control) per the roadmap design spec:

1. `allowed_domains` spider argument
2. Stem-aware keyword matching
3. Sitemap seed loader CLI
4. Blended FTS + relevance ranking

See `docs/superpowers/specs/2026-07-13-grawlerx-roadmap-design.md` for Phase 3–4 details. A separate implementation plan should be written before starting Phase 3.
