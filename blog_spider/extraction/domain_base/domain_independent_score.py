#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 7:03 AM'

from blog_spider.config import config
from pymongo import MongoClient, InsertOne
from pymongo.collection import Collection
from bs4 import BeautifulSoup
import hashlib
import re
import math


def md5hash(word: str):
    return hashlib.md5(word.encode()).hexdigest()[0:12]


def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    coll: Collection = client.spider.extend_raw_doc_2020_04_29
    ds_map_record = client.spider.domain_sentence_map.find_one({"domain": domain})
    ds_map = ds_map_record['map']
    domain_independent_score: Collection = client.spider.domain_independent_score
    opts = []
    for doc in coll.find({"domain": domain}):
        html = doc['html']
        soup = BeautifulSoup(html, "html5lib")
        text = soup.text
        words = re.split("\W", text)
        word_count = 0
        score = 0
        for word in words:
            word = word.strip()
            if word == "":
                continue
            h = md5hash(word)
            rate = ds_map.get(h)
            score += math.exp(-rate)
            word_count += 1
        domain_score = 0 if word_count == 0 else score / word_count
        opts.append(InsertOne({
            "incid": doc['incid'],
            'url': doc['url'],
            'domain': domain,
            'score': domain_score
        }))
    domain_independent_score.bulk_write(opts)


def process_all():
    client = MongoClient(config.spider_mongo_str)
    domain_sentence_map: Collection = client.spider.domain_sentence_map
    domains = list(domain_sentence_map.aggregate([{'$group': {"_id": "$domain"}}]))
    for data in domains:
        domain = data['_id']
        process_domain(domain)


if __name__ == '__main__':
    process_all()
    pass
