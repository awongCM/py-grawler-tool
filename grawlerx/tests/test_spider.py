import pytest
from scrapy import Request
from scrapy.http import HtmlResponse, TextResponse
from scrapy.utils.test import get_crawler

from grawlerx.spiders.search_crawler import SearchCrawler


def test_spider_parses_max_depth_argument():
    crawler = get_crawler(SearchCrawler)
    spider = SearchCrawler.from_crawler(crawler, max_depth="3")

    assert spider.max_depth == 3


def test_init_requires_keywords():
    with pytest.raises(ValueError, match="At least one keyword"):
        SearchCrawler(keywords="")


def test_parse_skips_non_html_responses():
    crawler = get_crawler(SearchCrawler)
    spider = SearchCrawler.from_crawler(crawler, keywords="cattle")
    response = TextResponse(
        url="https://example.com/feed.json",
        body=b'{"items": []}',
        headers={"Content-Type": "application/json"},
        request=Request("https://example.com/feed.json"),
    )

    assert list(spider.parse(response)) == []


def test_parse_yields_item_for_relevant_html():
    crawler = get_crawler(SearchCrawler)
    spider = SearchCrawler.from_crawler(crawler, keywords="cattle", min_score="0.1")
    html = b"""
    <html>
      <head><title>Cattle history</title></head>
      <body><p>Cattle were domesticated long ago.</p></body>
    </html>
    """
    response = HtmlResponse(
        url="https://example.com/cattle",
        body=html,
        request=Request("https://example.com/cattle"),
    )

    results = list(spider.parse(response))
    items = [result for result in results if not isinstance(result, Request)]

    assert len(items) == 1
    assert items[0]["url"] == "https://example.com/cattle"
    assert items[0]["relevance_score"] > 0


def test_parse_does_not_follow_links_at_max_depth():
    crawler = get_crawler(SearchCrawler)
    spider = SearchCrawler.from_crawler(crawler, keywords="cattle", max_depth="0")
    html = b"""
    <html>
      <head><title>Cattle history</title></head>
      <body>
        <p>Cattle were domesticated long ago.</p>
        <a href="/more-cattle">More cattle</a>
      </body>
    </html>
    """
    response = HtmlResponse(
        url="https://example.com/cattle",
        body=html,
        request=Request("https://example.com/cattle", meta={"depth": 0}),
    )

    results = list(spider.parse(response))
    follow_requests = [result for result in results if isinstance(result, Request)]

    assert follow_requests == []
