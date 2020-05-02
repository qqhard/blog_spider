#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/2 8:19 AM'

from pymongo import MongoClient
from pymongo.collection import Collection
from blog_spider.config import config
import random
from functools import reduce
import pandas as pd
from blog_spider.util.list import resize

sample_num = 500


def pre_process(domain_data):
    for idx, item in enumerate(domain_data['items']):
        cdata = item['condense_data']
        l = len(cdata) - 1
        i = l
        while i > 0:
            nc = []
            for c in cdata[i]:
                if c in cdata[i - 1]:
                    continue
                nc.append(c)
            if (not nc) and i == l:
                cdata.pop()
                l -= 1
            else:
                cdata[i] = nc
            i -= 1
        item['condense_data'] = cdata
        domain_data['items'][idx] = item


def cal_distance(x, y):
    lx = len(x)
    ly = len(y)
    lm = max(lx, ly)
    dis = 0
    for i in range(0, lm - 1):
        if i >= lx:
            dis += y[i]
        elif i >= ly:
            dis += x[i]
        else:
            dis += abs(y[i] - x[i])
    return dis


def get_threshold_distance(vectors):
    l = len(vectors)
    if l < 2:
        return 0
    sum = 0
    diss = []
    for _ in range(sample_num):
        ia = random.randint(0, l - 1)
        ib = ia
        while ib == ia:
            ib = random.randint(0, l - 1)
        dis = cal_distance(vectors[ia],vectors[ib])
        sum += dis
        diss.append(dis)
    diss.sort()
    threshold = reduce(lambda x, y: x + y, diss[0:500], 0) / 500
    return threshold


def process_domain_test(domain_data):
    threshold, diss = get_threshold_distance(domain_data)
    print(threshold)
    diss.sort()
    for i, dis in enumerate(diss):
        print(i, dis)



def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    coll: Collection = client.spider.vector_domain
    vectors = []
    identifys= []
    for vdata in coll.find({"domain":domain}):
        vectors.append(vdata['condense_data'])
        identifys.append((vdata['url'],vdata['incid']))
    threshold = get_threshold_distance(vectors)
    clusters = []
    for i,vector in enumerate(vectors) :
        nc = True
        for cluster in clusters:
            for identify,svector in cluster :
                if cal_distance(vector,svector) < threshold :
                    nc = False
                    cluster.append((identifys[i],vector))
                break
        if nc is True :
            clusters.append([(identifys[i],vector)])
    clusters = list(map(lambda x : list(map(lambda y:y[0],x)),clusters))
    return clusters

def process_all():
    client = MongoClient(config.spider_mongo_str)
    vdata : Collection = client.spider.vector_domain
    coll_cluster :Collection = client.domain_cluster
    domains = list(vdata.aggregate([{'$group': {"_id": "$domain"}}]))
    for data in domains :
        domain = data['_id']
        res = process_domain(domain)
        coll_cluster.insert_one({"domain":domain,"cluster":res})

if __name__ == '__main__':
    process_all()
