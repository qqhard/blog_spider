#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 7:03 AM'

from blog_spider.config import config
from pymongo import MongoClient
from pymongo.collection import  Collection
from bs4 import BeautifulSoup
import hashlib
import re



def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    coll : Collection = client.spider.extend_raw_doc_2020_04_29
    ds_map_record = client.spider.domain_sentence_map.find_one({"domain":domain})
    ds_map = ds_map_record['map']
    for doc in coll.find({"domain":domain}):
        pass


    pass



if __name__ == '__main__':
    pass


