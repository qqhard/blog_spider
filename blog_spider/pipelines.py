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
        self.candi_domain = self.client.spider.candidate_domain

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        domain = item['domain']
        if self.candi_domain.find_one({'domain': domain}) is None:
            self.candi_domain.insert_one({'domain': domain, 'url': item['url'], 'status': 0})
        return item
