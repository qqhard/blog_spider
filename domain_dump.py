import pymongo
import json

client = pymongo.MongoClient(host='localhost', port=27017)

arr = []

for o in client.spider.candidate_domain.find({'status': {'$gt': 0}}):
    d = {}
    if o.get('title') is not None:
        d['domain'] = o['domain']
        d['title'] = o['title']
        d['status'] = o['status']
        d['text'] = o['text']
        arr.append(d)

print(json.dumps(arr))
