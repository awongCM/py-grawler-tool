# py-grawler-tool

A small Scrapy-based web crawler that discovers keyword-relevant pages, stores them in a local SQLite FTS5 index, and exposes a minimal search API.

This repo focuses on the **crawl + index + search internals** for learning purposes. It is not meant to compete with production search engines.

## What it does

1. **Keyword crawl** — starts from seed URLs, scores each page for keyword relevance, and follows promising outbound links up to a configurable depth.
2. **Local index** — persists title, description, body text, and relevance score in SQLite with an FTS5 full-text index.
3. **Search API** — serves keyword queries over the indexed pages via FastAPI.

## Project layout

```text
grawlerx/
  grawlerx/
    spiders/search_crawler.py   # keyword-aware crawler
    keyword_search.py           # relevance scoring + FTS query builder
    storage.py                  # SQLite + FTS5 persistence
    search_service.py           # read-side search service
    api.py                      # HTTP API
  urls_with_cow_keywords.txt    # sample seed URLs
  data/grawlerx.db              # generated at runtime
```

## Setup

```bash
cd grawlerx
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run a crawl

```bash
python -m grawlerx crawl --keywords "cow,cattle" --max-depth 1
```

Optional flags:

- `--seeds-file` path to a newline-delimited URL list
- `--min-score` minimum relevance score before a page is stored (default `0.15`)
- `--max-depth` link-follow depth from each seed (default `1`)

## Search the index

CLI:

```bash
python -m grawlerx search "cattle"
```

HTTP API:

```bash
python -m grawlerx serve --host 0.0.0.0 --port 8000
curl "http://localhost:8000/search?q=cattle"
curl "http://localhost:8000/health"
```

The API binds to `127.0.0.1` by default for local use. Pass `--host 0.0.0.0` when deploying behind a proxy.

## Search in the browser

```bash
python -m grawlerx serve
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/), search, and view results at `/results?q=...`.

The JSON API remains available at `/search?q=...` for programmatic use.

## Tests

```bash
cd grawlerx
pytest -q
```

## Still out of scope

- Large-scale distributed crawling
- Production-grade ranking or freshness

## License

MIT — see [LICENSE](LICENSE).
