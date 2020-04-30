from urllib.parse import urlparse
from scrapy.http.request import Request
from blog_spider.util.doc_increment import get_domain_inc, redis_domain_inc
from scrapy_redis.dupefilter import RFPDupeFilter


class DomainDupeFilter(RFPDupeFilter):

    def __init__(self, server, key, debug=False):
        self.MAX_DOMAIN_DOWNLOAD = 2000
        super(DomainDupeFilter, self).__init__(server, key, debug)

    def request_seen(self, request: Request):
        url = request.url
        parse_url = urlparse(url)
        domain = parse_url.hostname
        if get_domain_inc(domain) > self.MAX_DOMAIN_DOWNLOAD:
            return True
        res = super(DomainDupeFilter, self).request_seen(request)
        if res is False:
            redis_domain_inc(domain)
        return res
