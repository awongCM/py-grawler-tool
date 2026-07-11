import pytest
from fastapi.testclient import TestClient

from grawlerx.api import app, get_search_service
from grawlerx.storage import init_db, upsert_page


def test_api_search_and_health(tmp_path, monkeypatch):
    db_path = tmp_path / "api.db"
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

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["indexed_pages"] == 1

    search = client.get("/search", params={"q": "cattle"})
    assert search.status_code == 200
    payload = search.json()
    assert payload["count"] == 1
    assert payload["results"][0]["url"] == "https://example.com/cattle"

    get_search_service.cache_clear()
