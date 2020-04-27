# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.response import get_base_url
from scrapy import Request
from urllib.parse import urljoin
from blog_spider.items import RawHtmlItem
from blog_spider.config.LocalConfig import config
import pymongo
import re

domain_pa = re.compile(r"https?://(.*?)[\/\?\#]")


class ExtendDomainSpider(scrapy.Spider):
    name = 'extend_domain_spider'

    def __init__(self):
        client = pymongo.MongoClient(config.spider_mongo_str)
        collec_domain = client.spider.candidate_domain
        # collec_new_domain = client.spider.new_domain
        allowed_domains = []
        start_urls = []
        for o in collec_domain.find({'status':1}):
            domain = o.get('domain')
            allowed_domains.append(domain)
            start_urls.append(o.get('url'))
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls

    def parse(self, response):
        base_url = get_base_url(response)
        hrefs = response.xpath('//a/@href').extract()
        domain = domain_pa.match(base_url).group(1)
        for url in hrefs:
            full_url = urljoin(base_url, url)
            domain_res = domain_pa.match(full_url)
            if domain_res is not None and domain_res.group(1) in self.allowed_domains:
                yield Request(full_url, self.parse)

        url = urljoin(base_url, response.url)
        item = RawHtmlItem()
        item['url'] = url
        item['html'] = response.text
        item['domain'] = domain

        yield item
