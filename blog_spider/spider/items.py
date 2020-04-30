# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class BlogSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()
    title = Field()
    text = Field()


class RawHtmlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()
    html = Field()
    domain = Field()
    incid = Field()

class DomainLinkItem(scrapy.Item):
    url = scrapy.Field()
    domain = scrapy.Field()
