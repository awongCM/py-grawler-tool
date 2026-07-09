import scrapy


class CrawledPageItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    body = scrapy.Field()
    relevance_score = scrapy.Field()
    keywords = scrapy.Field()
