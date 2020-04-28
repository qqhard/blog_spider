import re
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag, PreformattedString
from pymongo import MongoClient

from blog_spider.config import config

no_content_tags = ['script', 'style', 'svg', 'br', 'hr', 'area', 'base', 'img', 'input', 'link', 'meta', 'param', 'col',
                   'font', 'center']
xpath_skip_tags = ["body", "p", "a", "pre", 'span', 'b', 'strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr', 'th', 'td']

escape_re = r'([\+.~`@#%&=\'\\:;<>,/\(\)])'
escape_replace = r'\\\1'
tag_distance_limit = 4


def extraction_content(soup: BeautifulSoup):
    contents = []
    body = soup.body
    if body is None:
        return "", ""

    def get_new_path(tag: Tag, xpath):

        if tag.name in xpath_skip_tags:
            return xpath

        add_xpath = tag.name
        id = tag.attrs.get("id")
        # if id is not None and tag.name != "p":
        #     add_xpath = add_xpath + "#" + str.strip(re.sub(escape_re, escape_replace, id))
        clss = tag.attrs.get("class")
        if clss is not None and tag.name != "p":
            for cls in clss:
                add_xpath = add_xpath + "." + str.strip(re.sub(escape_re, escape_replace, cls))
                break
        if add_xpath != "":
            xpath = xpath + ("" if xpath == "" else " ") + add_xpath
        return xpath

    # 根据路径 找到内容
    def dfs_for_contents(content, xpath: str):
        if content is None:
            return
        if isinstance(content, PreformattedString):
            return
        if isinstance(content, str):
            content = content.strip()
            content != "" and contents.append((xpath, content.strip()))
            return
        tag: Tag = content
        if tag.name in no_content_tags:
            return
        nxpath = get_new_path(tag, xpath)
        for tag_content in tag.contents:
            dfs_for_contents(tag_content, nxpath)

    dfs_for_contents(body, "")
    if not contents:
        return "", ""

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
    max_tags = []

    def dfs_for_max_tags(content, xpath):
        if content is None or isinstance(content, str):
            return
        tag: Tag = content
        new_xpath = get_new_path(tag, xpath)
        if new_xpath == max_path:
            max_tags.append(tag)
            return
        for c in tag.contents:
            dfs_for_max_tags(c, new_xpath)

    dfs_for_max_tags(body, "")

    # 标定每个内容离最选择路径的距离

    def dfs_for_distance(tag, dis):
        if tag is None:
            return
        if isinstance(tag, str):
            return
        if hasattr(tag, "min_distance") and tag.min_distance is not None and tag.min_distance <= dis:
            return
        if tag.name in xpath_skip_tags:
            dis = max(0, dis - 1)
        tag.min_distance = dis

        for content in tag.contents:
            dfs_for_distance(content, 0 if dis == 0 else dis + 1)
        if tag.parent is not None:
            dfs_for_distance(tag.parent, dis + 1)

    for tag in max_tags:
        dfs_for_distance(tag, 0)
    res = []

    def dfs_for_result(tag, dis):
        if tag is None:
            return
        if isinstance(tag, PreformattedString):
            return
        if isinstance(tag, str):
            if dis > tag_distance_limit:
                return
            resc = tag.strip()
            resc != "" and res.append(resc)
            return
        if tag.name in no_content_tags:
            return
        tag: Tag = tag
        for c in tag.contents:
            dfs_for_result(c, tag.min_distance)

    dfs_for_result(body, body.min_distance)

    return "\n".join(res), max_path


def run_all():
    argv = sys.argv
    start_id = 0
    if len(argv) > 1:
        try:
            start_id = int(argv[1])
        except Exception:
            pass

    client = MongoClient(config.spider_mongo_str)
    spider = client.spider
    erdoc = spider.extend_raw_doc
    rough_data = spider.rough_data
    for doc in erdoc.find({"incid": {"$gt": start_id}}):
        try:
            html = doc['html']
            soup:BeautifulSoup = BeautifulSoup(html,"html5lib")
            (res, max_path) = extraction_content(soup)
            title = "" if soup.title is None else soup.title.text
            rough_data.insert_one({
                "incid": doc['incid'],
                "url": doc['url'],
                "domain": doc['domain'],
                "title":title,
                "max_path": max_path,
                "text": res,

            })
        except Exception as e:
            print(doc['incid'])
            print(e)
            raise e


def debug():
    client = MongoClient(config.spider_mongo_str)
    spider = client.spider
    erdoc = spider.extend_raw_doc
    # for doc in erdoc.find({"domain": "www.mosq.cn"}):
    for doc in erdoc.find({"incid": 302}):
        html = doc['html']
        soup = BeautifulSoup(html,'html5lib')
        title = "" if soup.title is None else soup.title.text
        res, max_path = extraction_content(soup)
        print(res)

if __name__ == '__main__':
    run_all()

