# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.response import get_base_url
from scrapy import Request
from urllib.parse import urljoin
from blog_spider.config import config
from blog_spider.spider.items import DomainLinkItem
import pymongo
import re

domain_pa = re.compile(r'https?://[\w.]+?\.[a-z]+/?$')
domain_pa2 = re.compile(r'https?://([\w.]+?)/?$')


class ExtendDomainSpider(scrapy.Spider):
    name = 'extend_domain_spider'

    def __init__(self):
        client = pymongo.MongoClient(config.spider_mongo_str)
        collec_domain = client.spider.candidate_domain
        # collec_new_domain = client.spider.new_domain
        allowed_domains = []
        start_urls = []
        for o in collec_domain.find({'status': 1, 'title': {'$ne': None}}):
            domain = o.get('domain')
            allowed_domains.append(domain)
            start_urls.append(o.get('url'))
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls

    def parse(self, response):
        base_url = get_base_url(response)
        hrefs = response.xpath('//a/@href').extract()
        for url in hrefs:
            full_url = urljoin(base_url, url)
            yield Request(full_url, self.parse)

            m = domain_pa.match(url)
            if m is not None:
                m = domain_pa2.match(url)
                domain = m.group(1)
                item = DomainLinkItem()
                item['url'] = url
                item['domain'] = domain
                yield item
