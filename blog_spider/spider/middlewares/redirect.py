from scrapy.downloadermiddlewares.redirect import MetaRefreshMiddleware, RedirectMiddleware
from scrapy.utils.response import get_meta_refresh, get_base_url
from urllib.parse import urlparse, urljoin
from w3lib.url import safe_url_string


class MetaRefreshDomainMiddleware(MetaRefreshMiddleware):

    def __init__(self, *args, **kwargs):
        super(MetaRefreshDomainMiddleware, self).__init__(*args, **kwargs)

    def process_response(self, request, response, spider):
        base_url = get_base_url(response)
        interval, url = get_meta_refresh(response, ignore_tags=self._ignore_tags)
        if urlparse(base_url).hostname == urlparse(url).hostname:
            return super(MetaRefreshDomainMiddleware, self).process_response(request, response, spider)
        return response


class RedirectDomainMiddleware(RedirectMiddleware):
    def __init__(self, *args, **kwargs):
        super(RedirectDomainMiddleware, self).__init__(*args, **kwargs)

    def process_response(self, request, response, spider):
        if (request.meta.get('dont_redirect', False) or
                response.status in getattr(spider, 'handle_httpstatus_list', []) or
                response.status in request.meta.get('handle_httpstatus_list', []) or
                request.meta.get('handle_httpstatus_all', False)):
            return response

        allowed_status = (301, 302, 303, 307, 308)
        if 'Location' not in response.headers or response.status not in allowed_status:
            return response

        location = safe_url_string(response.headers['Location'])
        if response.headers['Location'].startswith(b'//'):
            request_scheme = urlparse(request.url).scheme
            location = request_scheme + '://' + location.lstrip('/')
        redirected_url = urljoin(request.url, location)
        base_url = get_base_url(response)
        if urlparse(base_url).hostname != urlparse(redirected_url).hostname:
            return response

        if response.status in (301, 307, 308) or request.method == 'HEAD':
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        redirected = self._redirect_request_using_get(request, redirected_url)
        return self._redirect(redirected, request, spider, response.status)
