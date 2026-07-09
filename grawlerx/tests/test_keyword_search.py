from grawlerx.keyword_search import build_fts_query, link_is_promising, score_page


def test_score_page_weights_title_higher_than_body():
    high_title = score_page(["cattle"], title="Cattle origins", body="unrelated text")
    high_body = score_page(["cattle"], title="Origins", body="cattle cattle cattle")
    assert high_title > 0
    assert high_title >= high_body


def test_link_is_promising_matches_url_or_anchor():
    assert link_is_promising("https://example.com/cattle", "", ["cattle"])
    assert link_is_promising("https://example.com/page", "learn about cows", ["cow"])
    assert not link_is_promising("https://example.com/page", "unrelated", ["cow"])


def test_build_fts_query_quotes_terms():
    assert build_fts_query("cow cattle") == '"cow" "cattle"'
