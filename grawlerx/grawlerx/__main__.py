"""CLI helpers for running crawls and local search."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from grawlerx.search_service import SearchService


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grawlerx crawl and search utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    crawl_parser = subparsers.add_parser("crawl", help="Run the keyword search crawler")
    crawl_parser.add_argument("--keywords", default="cow,cattle")
    crawl_parser.add_argument("--seeds-file", default=None)
    crawl_parser.add_argument("--min-score", default="0.15")
    crawl_parser.add_argument("--max-depth", default="1")

    search_parser = subparsers.add_parser("search", help="Query the local crawl index")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10)

    serve_parser = subparsers.add_parser("serve", help="Start the search API")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "crawl":
        return _run_crawl(args)
    if args.command == "search":
        return _run_search(args)
    if args.command == "serve":
        return _run_serve(args)
    return 1


def _run_crawl(args: argparse.Namespace) -> int:
    project_root = Path(__file__).resolve().parent.parent
    command = [
        sys.executable,
        "-m",
        "scrapy",
        "crawl",
        "search-crawler",
        "-a",
        f"keywords={args.keywords}",
        "-a",
        f"min_score={args.min_score}",
        "-a",
        f"max_depth={args.max_depth}",
    ]
    if args.seeds_file:
        command.extend(["-a", f"seeds_file={args.seeds_file}"])

    completed = subprocess.run(command, cwd=project_root, check=False)
    return completed.returncode


def _run_search(args: argparse.Namespace) -> int:
    service = SearchService()
    results = service.search(args.query, limit=args.limit)
    print(json.dumps({"query": args.query, "results": results}, indent=2))
    return 0


def _run_serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("grawlerx.api:app", host=args.host, port=args.port, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
