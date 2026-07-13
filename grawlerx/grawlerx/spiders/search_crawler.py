from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin, urlparse

from scrapy import Request
from scrapy.spiders import Spider

from grawlerx.items import CrawledPageItem
from grawlerx.keyword_search import link_is_promising, parse_keywords, score_page

DEFAULT_SEEDS_FILE = Path(__file__).resolve().parents[2] / "urls_with_cow_keywords.txt"


class SearchCrawler(Spider):
    name = "search-crawler"
    start_urls: list[str] = []

    # Depth is enforced in parse(); Scrapy's middleware is disabled (0 = no limit).
    custom_settings = {
        "DEPTH_LIMIT": 0,
    }

    def __init__(
        self,
        keywords: str = "cow,cattle",
        seeds_file: str | None = None,
        min_score: str = "0.15",
        max_depth: str = "1",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.keywords = parse_keywords(keywords)
        self.min_score = float(min_score)
        self.max_depth = int(max_depth)
        self.seeds_path = Path(seeds_file) if seeds_file else DEFAULT_SEEDS_FILE
        self.start_urls = self._load_seed_urls()

        if not self.keywords:
            raise ValueError(
                "At least one keyword is required (e.g. -a keywords=cow,cattle)"
            )

    def _load_seed_urls(self) -> list[str]:
        if not self.seeds_path.exists():
            self.logger.warning("Seed file not found: %s", self.seeds_path)
            return []

        urls: list[str] = []
        with self.seeds_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                url = line.strip()
                if not url or url.startswith("#"):
                    continue
                if self.keywords and not link_is_promising(url, "", self.keywords):
                    continue
                urls.append(url)
        return urls

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta={"depth": 0})

    def parse(self, response):
        if response.status >= 400:
            return

        content_type = (response.headers.get("Content-Type") or b"").decode("latin-1").lower()
        if content_type and "html" not in content_type:
            return

        title = self._extract_title(response)
        description = self._extract_description(response)
        body = self._extract_body_text(response)
        relevance = score_page(
            self.keywords,
            title=title,
            description=description,
            body=body,
            url=response.url,
        )

        if relevance >= self.min_score:
            item = CrawledPageItem()
            item["url"] = response.url
            item["title"] = title
            item["description"] = description
            item["body"] = body
            item["relevance_score"] = relevance
            item["keywords"] = ",".join(self.keywords)
            yield item

        depth = int(response.meta.get("depth", 0))
        if depth >= self.max_depth:
            return

        for href, anchor_text in self._extract_links(response):
            if not link_is_promising(href, anchor_text, self.keywords):
                continue
            yield response.follow(
                href,
                callback=self.parse,
                meta={"depth": depth + 1},
            )

    @staticmethod
    def _extract_title(response) -> str:
        values = response.xpath("//title/text()").getall()
        return " ".join(value.strip() for value in values if value.strip())

    @staticmethod
    def _extract_description(response) -> str:
        values = response.xpath("//meta[@name='description']/@content").getall()
        return " ".join(value.strip() for value in values if value.strip())

    @staticmethod
    def _extract_body_text(response) -> str:
        paragraphs = response.xpath("//p//text()").getall()
        return " ".join(chunk.strip() for chunk in paragraphs if chunk.strip())

    @staticmethod
    def _extract_links(response) -> list[tuple[str, str]]:
        links: list[tuple[str, str]] = []
        for anchor in response.css("a[href]"):
            href = anchor.attrib.get("href", "").strip()
            if not href or href.startswith("#") or href.lower().startswith("javascript:"):
                continue
            absolute_url = urljoin(response.url, href)
            parsed = urlparse(absolute_url)
            if parsed.scheme not in {"http", "https"}:
                continue
            anchor_text = " ".join(text.strip() for text in anchor.css("::text").getall())
            links.append((absolute_url, anchor_text))
        return links
