#!
# __author__ = 'valseek'
# __create_time__ = '2020/4/30 4:06 AM'

from pymongo import MongoClient
from pymongo.collection import Collection
from blog_spider.config import config
from bs4 import BeautifulSoup
from bs4.element import Tag


def get_data(html, url, domain):
    soup = BeautifulSoup(html, "html5lib")

    cls_dic = {}

    def dfs_for_class_count(tag):
        if not isinstance(tag, Tag):
            return
        tag: Tag = tag
        clss = tag.attrs.get("class", [])
        for cls in clss:
            if cls_dic.get(cls) is None:
                cls_dic[cls] = 1
            else:
                cls_dic[cls] += 1
        for content in tag.contents:
            dfs_for_class_count(content)


    dfs_for_class_count(soup)

    print(cls_dic)


def process_domain(domain: str):
    client = MongoClient(config.spider_mongo_str)
    coll: Collection = client.spider.extend_raw_doc_2020_04_29
    for doc in coll.find({"domain": domain}):
        get_data(doc['html'], doc['url'], doc['domain'])


if __name__ == '__main__':
    test_domain = "blog.imalan.cn"
    process_domain(test_domain)
    pass
