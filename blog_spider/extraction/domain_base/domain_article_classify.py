#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 7:58 AM'

from blog_spider.config import config
from pymongo import MongoClient
from pymongo.collection import Collection
from functools import reduce
from bs4 import BeautifulSoup
import hashlib
import re
import math


def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    dis : Collection = client.spider.domain_independent_score
    dcscore : Collection = client.spider.domain_cluster_score
    dscores = list(dcscore.find({"domain":domain}))
    dscores.sort(key=lambda x:x['score'][0])
    for score in dscores:
        cls = score['class']
        s = score['score']
        for data in dis.find({"domain":domain,"class":cls}):
            print(cls,s,data['incid'],data['score'],data['url'])
        print("\n"*5)



if __name__ == '__main__':
    # domain = "www.leetao94.cn"
    domain = "waxxh.me"
    res = process_domain(domain)
    print(res)
