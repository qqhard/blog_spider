# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.response import get_base_url
from scrapy import Request
from urllib.parse import urljoin
from blog_spider.items import RawHtmlItem
import pymongo
import re

domain_pa = re.compile(r"https?://(.*?)[\/\?\#]")


class AddDomainInfoSpider(scrapy.Spider):
    name = 'add_domain_info_spider'

    def __init__(self):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.collec_domain = self.client.spider.candidate_domain
        # collec_new_domain = client.spider.new_domain
        allowed_domains = []
        start_urls = []
        url_2_domain = {}
        # for o in self.collec_domain.find({"status": {"$gt": 0}}):
        for o in self.collec_domain.find({"status": 0, "title": None}):
            domain = o.get('domain')
            allowed_domains.append(domain)
            start_urls.append(o.get('url'))
            url_2_domain[o.get('url')] = domain
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        self.url_2_domain = url_2_domain

    def parse(self, response):
        url = response.url
        domain = self.url_2_domain.get(url)
        if domain is not None:
            title = response.xpath("/html/head/title/text()").extract()[0]
            text = response.xpath("//*/text()").extract()
            text = ''.join(text)
            # print('######', domain, title, text)
            self.collec_domain.update_one(
                {'domain': domain}
                , {'$set': {'title': title, 'text': text}}
            )
