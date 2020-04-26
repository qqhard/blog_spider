# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class BlogSpiderPipeline(object):

    collection_name = 'doc'

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client['blog']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item

class ExtendDomainPipeline(object):

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.raw_doc = self.client.spider.raw_doc_20200426

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.raw_doc.insert_one(dict(item))
        return item
