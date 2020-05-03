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
from pymongo import InsertOne

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
        dis = cal_distance(vectors[ia], vectors[ib])
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


def recore(core,  vector):
    lc = len(core)
    lv = len(vector)
    lm = max(lc, lv)
    newcore = [0] * lm

    for i in range(lm):
        if i < lc:
            newcore[i] += core[i] / 2
        if i < lv:
            newcore[i] += vector[i] / 2
    return newcore


def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    coll: Collection = client.spider.vector_domain
    vectors = []
    identifys = []
    for vdata in coll.find({"domain": domain}):
        vectors.append(vdata['condense_data'])
        identifys.append((vdata['url'], vdata['incid']))
    threshold = get_threshold_distance(vectors)
    cls_coll: Collection = client.spider.domain_clusters
    clusters = []
    ops = []

    for i, vector in enumerate(vectors):
        nc = True
        for k, core in enumerate(clusters):
            if cal_distance(core, vector) < threshold:
                ops.append(
                    InsertOne({"domain": domain, "url": identifys[i][0], "incid": identifys[i][1], "class": k + 1}))
                nc = False
                break

        if nc is True:
            clusters.append(vector)
            ops.append(
                InsertOne({"domain": domain, "url": identifys[i][0], "incid": identifys[i][1], "class": len(clusters)}))
    cls_coll.bulk_write(ops)
    return clusters


def process_all():
    client = MongoClient(config.spider_mongo_str)
    vdata: Collection = client.spider.vector_domain
    coll_cluster: Collection = client.spider.domain_cluster
    domains = list(vdata.aggregate([{'$group': {"_id": "$domain"}}]))
    for data in domains:
        domain = data['_id']
        res = process_domain(domain)
        coll_cluster.insert_one({"domain": domain, "cluster": res})


if __name__ == '__main__':
    process_all()
