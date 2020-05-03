#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/3 7:58 AM'

from blog_spider.config import config
from pymongo import MongoClient
from pymongo.collection import Collection
from functools import reduce
from bs4 import BeautifulSoup
import hashlib
import re
import math


def process_domain(domain):
    client = MongoClient(config.spider_mongo_str)
    domain_cluster: Collection = client.spider.domain_cluster
    domain_independent_score: Collection = client.spider.domain_independent_score

    # tmp = []
    #
    # for i in domain_independent_score.find({"domain":domain}):
    #     tmp.append((i['score'],i['url']))
    # tmp.sort(key=lambda x : x[0])
    # for i in tmp :
    #     print(i)
    # return []


    data = domain_cluster.find_one({"domain": domain})
    cluster = data['cluster']
    cluster_scores = []
    for i, s in enumerate(cluster):
        for url,incid in s :
            d = domain_independent_score.find_one({"incid":incid})
            print(i,incid,d['score'],url)

        ids = list(map(lambda x: x[1], s))
        if not ids:
            cluster_scores.append((i, 0))
            continue
        agg_res = domain_independent_score.aggregate([
                {"$match": {"incid": {"$in": ids}}},
                {"$group": {"_id": None, "sum": {"$sum": "$score"}}}
            ])
        agg_res = list(agg_res)
        sum = agg_res[0]['sum']
        cluster_scores.append((i,sum/len(ids)))
    cluster_scores.sort(key=lambda x:x[1])
    return cluster_scores


if __name__ == '__main__':
    # domain = "www.leetao94.cn"
    domain = "www.shephe.com"
    res = process_domain(domain)
    print(res)
