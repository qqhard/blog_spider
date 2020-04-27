from scrapy_redis.spiders import RedisCrawlSpider
from blog_spider.linkextractors import DomainLinkExtractor
from scrapy.spiders import Rule
from scrapy.http.response.html import HtmlResponse
from scrapy import Request
from scrapy.utils.response import get_base_url
from urllib.parse import urlparse, ParseResult, urljoin
from blog_spider.items import RawHtmlItem
from blog_spider.util.DocIncrement import redis_row_doc_num


class RedisExtendSpider(RedisCrawlSpider):
    redis_key = "blog:start_urls"
    name = "redis_craw_spider"

    rules = (
        Rule(DomainLinkExtractor(), callback='parse_page', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(RedisExtendSpider, self).__init__(*args, **kwargs)

        pass

    def parse_page(self, response: HtmlResponse):
        baseUrl = get_base_url(response)
        baseUrlParse: ParseResult = urlparse(baseUrl)
        domain = baseUrlParse.netloc
        item = RawHtmlItem()
        item['html'] = response.text
        item["incid"] = redis_row_doc_num()
        item['domain'] = domain
        item['url'] = urljoin(baseUrl, response.url)
        yield item