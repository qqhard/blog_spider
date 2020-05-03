#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 1:39 PM'

from blog_spider.config import config
from redis import Redis
from pymongo import MongoClient
from pymongo.collection import Collection

redis = Redis(**config.redis_conn, decode_responses=True)

cluster_cache_key = "DOMAIN_CLUSTER_KEY"

def cache_class():
    client = MongoClient(config.spider_mongo_str)
    coll : Collection = client.spider.domain_clusters
    for doc in coll.find():
        incid = doc['incid']
        cls = doc['class']
        redis.hset(cluster_cache_key,incid,cls)

def get_cluster(incid):
    res = redis.hget(cluster_cache_key,incid)
    return int(res)



if __name__ == '__main__':
    cache_class()


