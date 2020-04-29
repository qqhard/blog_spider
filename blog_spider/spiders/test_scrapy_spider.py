#!
# __author__ = 'valseek'
# __create_time__ = '2020/4/29 11:26 AM'

import scrapy
import sys

class TestScrapySpider(scrapy.Spider):

    name = "test_scrapy_spider"

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES_BASE": {
            'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
            'blog_spider.middlewares.redirect.MetaRefreshDomainMiddleware': 580,
            'blog_spider.middlewares.redirect.RedirectDomainMiddleware': 600,
        },
        "DOWNLOAD_HANDLERS_BASE":{
            'http': 'blog_spider.handler.ForceAcceptHTTPDownloadHandler',
            'https': 'blog_spider.handler.ForceAcceptHTTPDownloadHandler',
            'file': 'scrapy.core.downloader.handlers.file.FileDownloadHandler',
            's3': 'scrapy.core.downloader.handlers.s3.S3DownloadHandler',
            'ftp': 'scrapy.core.downloader.handlers.ftp.FTPDownloadHandler'
        },
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        "LOG_LEVEL":"DEBUG",
        "DOWNLOAD_TIMEOUT":10000,
        "LOG_FILE":None,
        "FORCE_ACCEPT":True,
    }

    def __init__(self):
        super(TestScrapySpider, self).__init__()
        # self.start_urls=["https://mirrors.aliyun.com/epel/8/Everything/x86_64/Packages/z/zabbix40-web-mysql-4.0.17-1.el8.noarch.rpm"]
        self.start_urls=["http://www.susubaby.cn"]
        pass

    def parse(self, response):
        print(response)
        pass

