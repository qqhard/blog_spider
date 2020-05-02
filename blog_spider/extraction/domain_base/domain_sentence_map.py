#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 6:32 AM'

from blog_spider.config import config
from pymongo import MongoClient
from pymongo.collection import  Collection
from bs4 import BeautifulSoup
import hashlib
import re



def md5hash(word:str) :
    return hashlib.md5(word.encode()).hexdigest()[0:12]





def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    coll :Collection = client.spider.extend_raw_doc_2020_04_29
    dic = {}
    for doc in coll.find({"domain":domain}):
        html = doc['html']
        soup = BeautifulSoup(html,"html5lib")
        text = soup.text
        words = re.split("\W",text)
        for word in words :
            h = md5hash(word)
            if dic.get(h) is None :
                dic[h] = 1
            else :
                dic[h] += 1
    return dic


def process_all():
    client = MongoClient(config.spider_mongo_str)
    coll :Collection = client.spider.extend_raw_doc_2020_04_29
    domains = list[coll.aggregate([{'$group': {"_id": "$domain"}}])]
    domain_sentence_map : Collection = client.spider.domain_sentence_map
    for data in domains :
        domain = data['_id']
        res = process_domain(domain)
        domain_sentence_map.insert_one({"domain":domain,"map":res})




if __name__ == '__main__':
    process_all()







