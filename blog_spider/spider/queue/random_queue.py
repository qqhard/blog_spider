#!
# __author__ = 'valseek'
# __create_time__ = '2020/4/30 5:41 AM'


from scrapy_redis.queue import Base
from redis import StrictRedis


class RandomQueue(Base):

    def __init__(self, server, spider, key, serializer=None):
        super(RandomQueue, self).__init__(server, spider, key, serializer)
        pass

    def __len__(self):
        return self.server.scard(self.key)

    def push(self, request):
        server: StrictRedis = self.server
        server.sadd(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        server: StrictRedis = self.server
        r = server.spop(self.key)
        if r is None:
            return None
        return self._decode_request(r)
