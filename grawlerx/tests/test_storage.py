from pathlib import Path

from grawlerx.search_service import SearchService
from grawlerx.storage import init_db, upsert_page


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
