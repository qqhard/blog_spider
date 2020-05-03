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





def process_domain(domain,cls):
    client = MongoClient(config.spider_mongo_str)
    coll :Collection = client.spider.extend_raw_doc_2020_04_29
    domain_sentence_map : Collection = client.spider.domain_sentence_map
    dcs : Collection = client.spider.domain_clusters
    dic = {}
    for cdoc in dcs.find({"domain":domain,"class":cls}):
        doc = coll.find_one({"incid":cdoc['incid']})
        html = doc['html']
        soup = BeautifulSoup(html,"html5lib")
        text = soup.text
        words = re.split("\W",text)
        for word in words :
            word = word.strip()
            if word == "" :
                continue
            h = md5hash(word)
            if dic.get(h) is None :
                dic[h] = 1
            else :
                dic[h] += 1
    domain_sentence_map.insert_one({
        "domain":domain,
        "class":cls,
        "map":dic
    })


def process_all():
    client = MongoClient(config.spider_mongo_str)
    dcs : Collection = client.spider.domain_clusters
    domains = list(dcs.aggregate([{'$group': {"_id": {"domain":"$domain","class":"$class"}}}]))
    for data in domains :
        domain = data['_id']['domain']
        cls = data['_id']['class']
        process_domain(domain,cls)

if __name__ == '__main__':
    process_all()







