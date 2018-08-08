# TODO

from scrapy.http.request import Request
from scrapy.spiders import Spider

class SearchCrawler(Spider):
  name = 'search-crawler'
  start_urls = []
  allowed_domains = ["example.com"]
  
  # populate the start urls dynamically
  # TODO - need to find a way to populate this using true keyword search
  with open('./urls_with_cow_keywords.txt', 'r') as urls:
    for url in urls:
      start_urls.append(url)
  
  # call the start_requests hook method
  def start_requests(self):
    for each_url in self.start_urls:
      new_url = reformat_url(each_url)
      yield Request(new_url, self.parse)

  def parse(self, response):
    try:
      yield {
      'url': response.url,
      'title': response.xpath("//title/text()")[0].extract(),
      'meta': response.meta,
      'description': response.xpath("//meta[@name='description']/@content")[0].extract(), # not all sites have this
      'body': response.body
    }  
    except (ValueError, IndexError):
      # print('Could not yield this response url - ' + response.url + '. Just yield the rest')
      yield {
        'url': response.url,
        'title': response.xpath("//title/text()")[0].extract(),
        'meta': response.meta
      }

# reformat urls
def reformat_url(url):
  # show the raw url format
  # print(url)
  return url.rstrip('\n')
