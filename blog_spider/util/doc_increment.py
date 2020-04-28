from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
from blog_spider.config import config
from redis import StrictRedis

client = MongoClient(config.spider_mongo_str)
redis = StrictRedis(**config.redis_conn,decode_responses=True)


def mongo_row_doc_num():
    inc: Collection = client.spider.increment
    res = inc.find_one_and_update({"key": "row_doc_count"}, {"$inc": {"value": 1}}, upsert=True,
                                  return_document=ReturnDocument.AFTER)
    return res.value


def redis_row_doc_num():
    row_num_key = "BLOG_SPIDER_ROW_DOC_INC_ID"
    return redis.incr(row_num_key)

def redis_domain_inc(domain):
    domain_inc_key = "BLOG_DOMAIN_INC_KEY"
    return int(redis.hincrby(domain_inc_key,domain,1))

def get_domain_inc(domain):
    domain_inc_key = "BLOG_DOMAIN_INC_KEY"
    res = redis.hget(domain_inc_key,domain)
    return 0 if res is None else int(res)

