#!
# __author__ = 'valseek'
# __create_time__ = '2020/4/29 2:52 PM'

from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from scrapy.core.downloader.handlers.http11 import ScrapyAgent
from scrapy.http.headers import Headers


class ForceAcceptScrapyAgent(ScrapyAgent):
    def __init__(self, contextFactory=None, connectTimeout=10, bindAddress=None, pool=None,
                 maxsize=0, warnsize=0, fail_on_dataloss=True, force_accept=False):
        self.force_accept = force_accept
        super(ForceAcceptScrapyAgent, self).__init__(contextFactory, connectTimeout, bindAddress, pool, maxsize,
                                                     warnsize, fail_on_dataloss)

    def _cb_bodyready(self, txresponse, request):
        if not self.force_accept:
            return super(ForceAcceptScrapyAgent, self)._cb_bodyready(txresponse, request)
        request_headers: Headers = request.headers
        response_herders: Headers = Headers(txresponse.headers.getAllRawHeaders())
        content_type: str = response_herders.get("content-type", b'').decode()
        accept_type: str = request_headers.get("accept", b'').decode()
        content_type = content_type.lower()
        accept_type = accept_type.lower()
        accept_type_list = accept_type.split(";")[0].split(",")
        content_type = content_type.split(";")[0].strip()
        d = request.response_defer if hasattr(request, "response_defer") else None
        if d is not None and not content_type in accept_type_list:
            d.cancel()
            txresponse.code = 406
            return [txresponse, b'', None, None]
        return super(ForceAcceptScrapyAgent, self)._cb_bodyready(txresponse, request)


class ForceAcceptHTTPDownloadHandler(HTTPDownloadHandler):

    def download_request(self, request, spider):
        """Return a deferred for the HTTP download"""
        agent = ForceAcceptScrapyAgent(
            contextFactory=self._contextFactory,
            pool=self._pool,
            maxsize=getattr(spider, 'download_maxsize', self._default_maxsize),
            warnsize=getattr(spider, 'download_warnsize', self._default_warnsize),
            fail_on_dataloss=self._fail_on_dataloss,
            force_accept=spider.settings.get("FORCE_ACCEPT", False)
        )
        d = agent.download_request(request)
        request.response_defer = d
        return d
