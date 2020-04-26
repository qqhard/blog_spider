import pymongo
from lxml import etree
import re

domain_pa = re.compile(r'https?://[\w.]+?\.[a-z]+/?$')
domain_pa2 = re.compile(r'https?://([\w.]+?)/?$')

client = pymongo.MongoClient(host='localhost', port=27017)

candi_urls = set([])

for doc in client.spider['raw_doc_20200426'].find():
    try:
        html = etree.HTML(doc.get('html'))
    except Exception as e:
        print(e)
    if html is None:
        continue
    result = html.xpath('//a/@href')
    for url in result:
        m = domain_pa.match(url)
        # print (url, m)
        if m is not None:
            candi_urls.add(m.group())

for url in candi_urls:
    m = domain_pa2.match(url)
    domain = m.group(1)
    print(domain)
    if client.spider.candidate_domain.find_one({'domain':domain}) is None:
        client.spider.candidate_domain.insert_one({'domain': m.group(1), 'url': url, 'status': 0})
