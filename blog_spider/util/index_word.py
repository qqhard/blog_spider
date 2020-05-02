#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/1 11:09 AM'

import random
from redis import Redis
from blog_spider.config import config

#   Warning
#   这个类不能用于分布式或者多多进程

class WordIndexer:

    def __init__(self, *args, **kwargs):
        self.key = kwargs.get("key", "iw_" + str(random.randint(10000, 99999)))
        self.server: Redis= Redis(**config.redis_conn, decode_responses=True)

    def get_index(self, word):
        res = self.server.hget(self.key,word)
        if res is not None :
            return int(res)
        while True :
            self.server.watch(self.key)
            hlen = self.server.hlen(self.key)
            self.server.execute_command("multi")
            self.server.hset(self.key,word,hlen)
            res = self.server.execute_command("exec")
            if res is not None :
                return hlen

    def get_dic(self):
        return self.server.hgetall(self.key)

    def __len__(self):
        return self.server.hlen(self.key)

    def __del__(self):
        self.server.delete(self.key)



