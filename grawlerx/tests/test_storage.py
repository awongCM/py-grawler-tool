from pathlib import Path

from grawlerx.search_service import SearchService
from grawlerx.storage import init_db, page_count, search_pages, upsert_page


def test_search_service_returns_indexed_page(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    upsert_page(
        url="https://example.com/cattle",
        title="Cattle domestication",
        description="How cows were domesticated",
        body="Cattle and cows spread across the world.",
        relevance_score=0.8,
        keywords="cow,cattle",
        db_path=db_path,
    )

    service = SearchService(db_path=db_path)
    results = service.search("cattle", limit=5)

    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/cattle"
    assert "Cattle" in results[0]["title"]


def test_upsert_updates_existing_page_and_search_index(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    upsert_page(
        url="https://example.com/cattle",
        title="Old title",
        description="Old description",
        body="Old body without keywords.",
        relevance_score=0.1,
        keywords="cow",
        db_path=db_path,
    )
    upsert_page(
        url="https://example.com/cattle",
        title="Cattle update",
        description="Updated cattle description",
        body="New cattle content.",
        relevance_score=0.9,
        keywords="cattle",
        db_path=db_path,
    )

    assert page_count(db_path) == 1
    results = search_pages("cattle", db_path=db_path)
    assert len(results) == 1
    assert results[0].title == "Cattle update"


def test_search_pages_returns_empty_for_blank_query(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    assert search_pages("   ", db_path=db_path) == []
