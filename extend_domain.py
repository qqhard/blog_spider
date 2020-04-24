import pymongo
from lxml import etree
import re

domain_pa = re.compile(r"https?://(.*?)[\/\?\#]")

client = pymongo.MongoClient(host='localhost', port=27017)

candi_urls = set([])

for doc in client.spider.raw_doc.find().limit(5):
    html = etree.HTML(doc.get('html'))
    result = html.xpath('//a/@href')
    for url in result:
        m = domain_pa.match(url)
        if m is not None:
            candi_urls.add(m.group(1))

print(candi_urls)
