#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 4:04 PM'


from pymongo import MongoClient
from pymongo.collection import Collection

from blog_spider.config import config
import math


def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    ds_map_record = client.spider.domain_sentence_map.find_one({"domain": domain})
    dcs: Collection = client.spider.domain_clusters
    dcm: Collection = client.spider.domain_cluster_map
    domain_cluster_score: Collection = client.spider.domain_cluster_score
    ds_map = ds_map_record['map']
    clss = list(dcs.aggregate([{"$match": {"domain": domain}}, {'$group': {"_id": {"class": "$class"}}}]))
    for cls_doc in clss:
        cls = cls_doc['_id']['class']
        map_doc = dcm.find_one({"domain": domain, "class": cls})
        dc_map :dict= map_doc['map']
        score = 0
        for key in dc_map :
            score += math.exp(-(ds_map[key]-dc_map[key]))
        kic = 0
        for key in ds_map :
            if dc_map.get(key) is not None:
                kic += 1

        score = score/len(dc_map)
        krate = kic/len(ds_map)
        domain_cluster_score.insert_one({
            "domain":domain,
            "class":cls,
            "score":[score,krate]
        })


def process_all():
    client = MongoClient(config.spider_mongo_str)
    dcm: Collection = client.spider.domain_cluster_map
    datas = list(dcm.aggregate([{'$group': {"_id": {"domain": "$domain"}}}]))
    for data in datas:
        process_domain(data['_id']['domain'])


if __name__ == '__main__':
    process_all()
