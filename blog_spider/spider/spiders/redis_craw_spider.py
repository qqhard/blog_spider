from scrapy_redis.spiders import RedisCrawlSpider
from blog_spider.spider.linkextractors import DomainLinkExtractor
from scrapy.spiders import Rule
from blog_spider.config import config
from scrapy.http.response.html import HtmlResponse
from scrapy.utils.response import get_base_url
from urllib.parse import urlparse, ParseResult, urljoin
from blog_spider.spider.items import RawHtmlItem
from blog_spider.util.doc_increment import redis_row_doc_num
import logging
import datetime

today = datetime.datetime.now()
log_file_path = "/var/log/blog_spider/log-{}-{}-{}.log".format(today.year, today.month, today.day)


class RedisExtendSpider(RedisCrawlSpider):
    redis_key = "blog:start_urls"
    name = "redis_craw_spider"
    custom_settings = {
        # 用来存储到mongodb
        "ITEM_PIPELINES": {
            'blog_spider.pipelines.DownloadDomainPipeline':300
        },
        # 使用scrapy_redis 的queue  dupefilter  scheduler and persist
        "SCHEDULER_QUEUE_CLASS": "blog_spider.spider.queue.RandomQueue",
        "DUPEFILTER_CLASS": "blog_spider.spider.filter.domain_dupefilter.DomainDupeFilter",
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "SCHEDULER_PERSIST": True,

        # 使用middlewares 让爬虫限定在 自己的domain 中
        "DOWNLOADER_MIDDLEWARES_BASE": {
            'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
            'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
            'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
            'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
            'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 560,
            'blog_spider.spider.middlewares.redirect.MetaRefreshDomainMiddleware': 580,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
            'blog_spider.spider.middlewares.redirect.RedirectDomainMiddleware': 600,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
            'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
            'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
        },
        # http downloader , 限定只下载网页
        "DOWNLOAD_HANDLERS_BASE": {
            'http': 'blog_spider.spider.handler.ForceAcceptHTTPDownloadHandler',
            'https': 'blog_spider.spider.handler.ForceAcceptHTTPDownloadHandler',
        },

        "REDIS_URL": config.redis_conn_str,
        "REDIS_START_URLS_KEY": "blog:start_urls",

        "FORCE_ACCEPT": True,
        # 只爬取网页
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        "RETRY_TIMES":8,
        "DOWNLOAD_DELAY":1,
        "RANDOMIZE_DOWNLOAD_DELAY":True,
        "DEPTH_LIMIT": 64,
        "LOG_LEVEL": logging.WARNING,
        "LOG_FILE": log_file_path,
        "DOWNLOAD_MAXSIZE":10485760, # 10M
        "DOWNLOAD_WARNSIZE":5242880, # 10M
        "CONCURRENT_REQUESTS":24,
        "REDIS_START_URLS_BATCH_SIZE":72

    }

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
