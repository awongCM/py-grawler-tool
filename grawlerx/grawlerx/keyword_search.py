"""Keyword relevance scoring for crawled pages."""

from __future__ import annotations

import re
from typing import Iterable, Sequence

WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)

# Title matches matter more than body text for simple keyword search.
FIELD_WEIGHTS = {
    "title": 3.0,
    "description": 2.0,
    "url": 1.5,
    "body": 1.0,
}


def parse_keywords(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [token.lower() for token in WORD_RE.findall(raw) if len(token) > 1]


def tokenize(text: str | None) -> set[str]:
    if not text:
        return set()
    return {token.lower() for token in WORD_RE.findall(text)}


def score_page(
    keywords: Sequence[str],
    *,
    title: str = "",
    description: str = "",
    body: str = "",
    url: str = "",
) -> float:
    """Return a 0-1 relevance score based on weighted keyword coverage."""
    if not keywords:
        return 0.0

    keyword_set = {keyword.lower() for keyword in keywords}
    fields = {
        "title": title,
        "description": description,
        "url": url,
        "body": body[:5000],
    }

    weighted_hits = 0.0
    total_weight = 0.0
    for field_name, field_value in fields.items():
        weight = FIELD_WEIGHTS[field_name]
        total_weight += weight
        field_tokens = tokenize(field_value)
        if field_tokens & keyword_set:
            weighted_hits += weight

    return round(weighted_hits / total_weight, 4) if total_weight else 0.0


def link_is_promising(url: str, anchor_text: str, keywords: Iterable[str]) -> bool:
    """Heuristic for whether a discovered link is worth fetching."""
    haystack = f"{url} {anchor_text}".lower()
    return any(keyword.lower() in haystack for keyword in keywords)


def build_fts_query(user_query: str) -> str:
    """Turn free text into a safe FTS5 AND query."""
    terms = parse_keywords(user_query)
    if not terms:
        return ""
    return " ".join(f'"{term}"' for term in terms)
