import sys
import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
client.spider.domain.create_Index({'domain': 1})

cmd = sys.argv[1]

if cmd == 'add_domain':
    domain = sys.argv[2]
    client.spider.domain.insert_one({'domain': domain})
elif cmd == 'list_domain':
    for o in client.spider.domain.find():
        print(o.get('domain'))
elif cmd == 'del_domain':
    domain = sys.argv[2]
    client.spider.domain.delete_one({'domain': domain})
elif cmd == 'update_domain':
    pass

