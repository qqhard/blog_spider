from pymongo import MongoClient
import redis

client = MongoClient("mongodb://spider:spider_f***man@mongo-server:27017")
redis = redis.StrictRedis(**{
    "host": "redis-server",
    "port": 6379
})

spider = client.spider
erdoc = spider.extend_raw_data
sdata = spider.scale_data
cdomain = spider.candidate_domain


for doc in cdomain.find():
    redis.lpush("blog:start_urls",doc['url'])
