import pymongo
from lxml import etree
import re

domain_pa = re.compile(r'https?://[\w.]+?/?$')

client = pymongo.MongoClient(host='localhost', port=27017)

candi_urls = set([])

for doc in client.spider.raw_doc.find():
    try:
        html = etree.HTML(doc.get('html'))
    except:
        print(doc.get('html'))
        continue
    result = html.xpath('//a/@href')
    for url in result:
        m = domain_pa.match(url)
        # print (url, m)
        if m is not None:
            candi_urls.add(m.group())

for i in candi_urls:
    print(i)
