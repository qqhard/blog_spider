
from blog_spider.config.common_config import __CommonConfig


class __LocalConfig(__CommonConfig) :
    def __init__(self):
        self.spider_mongo_str = "mongodb://localhost:27017"
        self.redis_conn_str = "redis://redis-server:6379"
        self.redis_conn = {
            "host" : "redis-server",
            "port" :6379
        }



config = __LocalConfig()
