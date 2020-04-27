# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from blog_spider.config.LocalConfig import config


class ExtendDomainPipeline(object):

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(config.spider_mongo_str)
        self.raw_doc = self.client.spider.extend_raw_doc

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.raw_doc.insert_one(dict(item))
        return item
