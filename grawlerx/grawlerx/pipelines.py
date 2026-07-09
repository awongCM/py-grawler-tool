from grawlerx.storage import init_db, upsert_page


class StoragePipeline:
    def open_spider(self, spider):
        init_db(spider.settings.get("GRAWLERX_DB_PATH"))

    def process_item(self, item, spider):
        upsert_page(
            url=item.get("url", ""),
            title=item.get("title", "") or "",
            description=item.get("description", "") or "",
            body=item.get("body", "") or "",
            relevance_score=float(item.get("relevance_score", 0.0) or 0.0),
            keywords=item.get("keywords", "") or "",
            db_path=spider.settings.get("GRAWLERX_DB_PATH"),
        )
        return item
