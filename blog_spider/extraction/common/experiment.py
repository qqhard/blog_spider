from pymongo import MongoClient
from pymongo.collection import Collection
from redis import StrictRedis
from bs4 import BeautifulSoup
from bs4.element import Tag
from blog_spider.config import config
import time


def extraction_content(soup: BeautifulSoup):
    contents = []
    body = soup.body

    # 根据路径 找到内容
    def dfs_for_contents(content, xpath: str):
        if isinstance(content, str):
            content = content.strip()
            content != "" and contents.append((xpath, content.strip()))
            return
        tag: Tag = content
        if tag.name == "script" or tag.name == "svg":
            return
        add_xpath = ""
        id = tag.attrs.get("id")
        if id is not None and tag.name != "p":
            add_xpath = add_xpath + "#" + id
        clss = tag.attrs.get("class")
        if clss is not None and tag.name != "p":
            for cls in clss:
                add_xpath = add_xpath + "." + cls
        if add_xpath != "":
            xpath = xpath + ("" if xpath == "" else " ") + add_xpath
        for tag_content in tag.contents:
            dfs_for_contents(tag_content, xpath)

    dfs_for_contents(body, "")

    # 找到最长内容的 选择路径
    dic = {}
    max_path = ""
    max_len = 0
    for tup in contents:
        if dic.get(tup[0]) is None:
            dic[tup[0]] = tup[1]
        else:
            dic[tup[0]] += "\n" + tup[1]
        if len(dic[tup[0]]) > max_len:
            max_len = len(dic[tup[0]])
            max_path = tup[0]
    max_tags = soup.select(max_path)

    # 标定每个内容离最选择路径的距离

    def dfs_for_distance(tag, dis):
        if isinstance(tag, str):
            return
        if hasattr(tag, "min_distance") and tag.min_distance is not None and tag.min_distance <= dis:
            return
        tag.min_distance = dis

        for content in tag.contents:
            dfs_for_distance(content, 0 if dis == 0 else dis + 1)
        if tag.parent is not None:
            dfs_for_distance(tag.parent, dis + 1)

    for tag in max_tags:
        dfs_for_distance(tag, 0)
    res = []

    def dfs_for_result(tag, dis):
        if isinstance(tag, str):
            if dis >4 :
                return
            resc = tag.strip()
            resc != "" and res.append(resc)
            return
        if tag.name in ["script"] :
            return
        tag: Tag = tag
        for c in tag.contents:
            dfs_for_result(c, tag.min_distance)

    dfs_for_result(body, body.min_distance)

    return "\n".join(res)


if __name__ == '__main__':

    client = MongoClient(config.spider_mongo_str)
    redis = StrictRedis(**config.redis_conn)
    spider = client.spider
    erdoc = spider.extend_raw_doc
    rough_data = spider.rough_data
    for doc in erdoc.find():
        try :
            html = doc['html']
            soup = BeautifulSoup(html, 'html.parser')
            res = extraction_content(soup)
            rough_data.insert_one({
                "incid":doc['incid'],
                "url" :doc['url'],
                "domain":doc['domain'],
                "text":res

                })
        except Exception as e :
            print(e)

    # doc = erdoc.find_one({})
    # html = doc['html']
    # soup = BeautifulSoup(html, 'html.parser')
    # res = extraction_content(soup)
    # print(res)
