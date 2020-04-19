# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.response import get_base_url
from scrapy import Request
from urllib.parse import urljoin
from blog_spider.items import BlogSpiderItem


class HexoSpiderSpider(scrapy.Spider):
    name = 'hexo_spider'
    allowed_domains = ['diygod.me','thief.one']
    start_urls = ['https://diygod.me/archives/','https://thief.one/archives/']

    def parse(self, response):
        base_url = get_base_url(response)
        if len(response.xpath('//*[contains(@class,"post-body")]')) > 0:
            title = response.xpath('//*[contains(@class,"post-title")]/text()').extract()
            text = response.xpath('//*[contains(@class,"post-body")]//text()').extract()
            url = urljoin(base_url, response.url)

            item = BlogSpiderItem()
            item['url'] = url
            item['title'] = title[0].strip()
            item['text'] = '\n'.join(text)
            yield item

        elif response.url.find('archives'):
            alabels = response.xpath('//a[contains(@class,"post-title-link")]/@href').extract()
            for url in alabels:
                full_path = urljoin(base_url, url)
                yield Request(full_path, self.parse)

            hrefs = response.xpath('//a/@href').extract()
            for url in hrefs:
                if url.find('archives') > 0:
                    full_path = urljoin(base_url, url)
                    print(full_path)
                    yield Request(full_path, self.parse)
