from urllib.parse import urlparse, ParseResult

from scrapy.linkextractors import LinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.http.response.html import HtmlResponse
from scrapy.link import Link
import logging


class DomainLinkExtractor(LinkExtractor):
    def __init__(self, *args, **kwargs):
        super(DomainLinkExtractor, self).__init__(*args, **kwargs)

    def extract_links(self, response: HtmlResponse):
        base_url = response.url
        base_url_parse_result: ParseResult = urlparse(base_url)
        domain = base_url_parse_result.hostname
        links = super(DomainLinkExtractor, self).extract_links(response)

        def domain_url_filter(link: Link):
            if link.nofollow:
                return False
            url_parse_result: ParseResult = urlparse(link.url)
            if url_parse_result.hostname == domain:
                logging.warning("{}\t-->\t{}".format(base_url, link.url))
                return True
            return False

        domain_links = list(filter(domain_url_filter, links))
        return domain_links
