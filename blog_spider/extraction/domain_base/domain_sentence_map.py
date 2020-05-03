#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 6:32 AM'

from blog_spider.config import config
from pymongo import MongoClient
from pymongo.collection import Collection
from bs4 import BeautifulSoup
import hashlib
import re


def md5hash(word: str):
    return hashlib.md5(word.encode()).hexdigest()[0:12]


def process_domain(domain, cls):
    client = MongoClient(config.spider_mongo_str)
    coll: Collection = client.spider.extend_raw_doc_2020_04_29
    domain_cluster_map: Collection = client.spider.domain_cluster_map
    dcs: Collection = client.spider.domain_clusters
    dic = {}
    for cdoc in dcs.find({"domain": domain, "class": cls}):
        doc = coll.find_one({"incid": cdoc['incid']})
        html = doc['html']
        soup = BeautifulSoup(html, "html5lib")
        text = soup.text
        words = re.split("\W", text)
        for word in words:
            word = word.strip()
            if word == "":
                continue
            h = md5hash(word)
            if dic.get(h) is None:
                dic[h] = 1
            else:
                dic[h] += 1
    domain_cluster_map.insert_one({
        "domain": domain,
        "class": cls,
        "map": dic
    })


def process_all():
    client = MongoClient(config.spider_mongo_str)
    dcs: Collection = client.spider.domain_clusters
    domains = list(dcs.aggregate([{'$group': {"_id": {"domain": "$domain", "class": "$class"}}}]))
    for data in domains:
        domain = data['_id']['domain']
        cls = data['_id']['class']
        process_domain(domain, cls)


def summer_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    dcm: Collection = client.spider.domain_cluster_map
    dsm :Collection = client.spider.domain_sentense_map

    dic = {}
    for data in dcm.find({"domain":domain}):
        m = data['map']
        for key in m :
            if dic.get(key) is None :
                dic[key] = m[key]
            else :
                dic[key] += m[key]
    dsm.insert_one({"domain":domain,"map":dic})




def summer_dict():
    client = MongoClient(config.spider_mongo_str)
    dcm: Collection = client.spider.domain_cluster_map
    datas = list(dcm.aggregate([{'$group': {"_id": {"domain": "$domain"}}}]))
    for data in datas:
        summer_domain(data['_id']['domain'])





if __name__ == '__main__':
    summer_dict()
