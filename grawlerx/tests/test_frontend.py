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
