#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/2 8:19 AM'

from pymongo import MongoClient
from pymongo.collection import Collection
from blog_spider.config import config
import random
from functools import reduce

decline = 0.7

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
    dec = 1
    for i in range(0, lm - 1):
        if i >= lx:
            dis += dec
        elif i >= ly:
            dis += dec
        else:
            sx = set(x[i])
            sy = set(y[i])
            dis += dec * (len(sx ^ sy)/len(sx | sy))
        dec *= decline
    return dis


def get_threshold_distance(domain_data):
    l = len(domain_data['items'])
    if l < 2:
        return 0
    sum = 0
    diss = []
    for _ in range(sample_num):
        ia = random.randint(0, l - 1)
        ib = ia
        while ib == ia:
            ib = random.randint(0, l - 1)
        dis = cal_distance(domain_data['items'][ia]['condense_data'], domain_data['items'][ib]['condense_data'])
        sum += dis
        diss.append(dis)
    diss.sort()
    threshold = reduce(lambda x, y: x + y, diss[0:300], 0) / 300
    return threshold


def process_domain_test(domain_data):
    pre_process(domain_data)
    threshold, diss = get_threshold_distance(domain_data)
    print(threshold)
    diss.sort()
    for i, dis in enumerate(diss):
        print(i, dis)


def process_domain(domain_data):
    pre_process(domain_data)
    threshold_distance = get_threshold_distance(domain_data)
    clusters = []
    for item in domain_data['items']:
        nc_flag = True
        for cluster in clusters:
            for itemx in cluster:
                dis = cal_distance(item['condense_data'], itemx['condense_data'])
                if dis < threshold_distance:
                    cluster.append(item)
                    nc_flag = False
                break
            if not nc_flag:
                break
        if nc_flag:
            clusters.append([item])
    for cluster in clusters:
        for item in cluster:
            print(item['url'], item['incid'])
            print(item['condense_data'])
            print('.' * 50)

        print("-" * 160, "\n" * 3)
    return clusters


if __name__ == '__main__':
    domain = "www.mosq.cn"
    client = MongoClient(config.spider_mongo_str)
    coll: Collection = client.spider.condense_raw

    data = coll.find_one({"domain": domain})
    # data = coll.find_one()
    process_domain(domain_data=data)
