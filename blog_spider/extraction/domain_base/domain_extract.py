#!
# __author__ = 'valseek'
# __create_time__ = '2020/4/30 4:06 AM'

from pymongo import MongoClient
from pymongo.collection import Collection
from blog_spider.config import config
from bs4 import BeautifulSoup
from bs4.element import Tag, PreformattedString
import re
from functools import reduce
from blog_spider.util.index_word import WordIndexer

no_content_tags = ['script', 'style', 'svg', 'br', 'hr', 'area', 'base', 'img', 'input', 'link', 'meta', 'param', 'col',
                   'font', 'center']

path_tags = ['body', 'div', 'section', 'main', 'nav', 'article','nav']

escape_re = r'([\+.~`@#%&=\'\\:;<>,/\(\)])'
escape_replace = r'\\\1'

indexer: WordIndexer = None




def get_new_path(tag: Tag, xpath):
    if tag.name not in path_tags:
        return xpath

    add_xpath = tag.name
    clss = tag.attrs.get("class")
    if clss is not None and tag.name != "p":
        for cls in clss:
            add_xpath = add_xpath + "." + str.strip(re.sub(escape_re, escape_replace, cls))
            break
    if add_xpath != "":
        xpath.append(add_xpath)
    return xpath


def get_path_content_func(contents=[]):
    def dfs_for_contents(content, xpath: str):
        if content is None:
            return contents
        if isinstance(content, PreformattedString):
            return contents
        if isinstance(content, str):
            content = content.strip()
            content != "" and contents.append((xpath[:], len(content.strip())))
            return contents
        tag: Tag = content
        if tag.name in no_content_tags:
            return contents
        nxpath = get_new_path(tag, xpath)
        for tag_content in tag.contents:
            dfs_for_contents(tag_content, nxpath[:])
        return contents

    return dfs_for_contents


def get_data(html, url, domain):
    soup = BeautifulSoup(html, "html5lib")
    contents = [] if soup.body is None else get_path_content_func([])(soup.body, [])
    content_dict = {}
    for path, content in contents:
        path = " ".join(path)
        content = content.strip()
        if content_dict.get(path) is None:
            content_dict[path] = [content]
        else:
            content_dict[path].append(content)
    path_rank = []
    for key in content_dict.keys():
        path_rank.append((reduce(lambda x, y: x + len(y), content_dict[key], 0), key))
    path_rank.sort(key=lambda x: x[0], reverse=True)
    return len(html), path_rank, url, domain


def get_condense_html_tree(html, *args, **kwargs):
    soup = BeautifulSoup(html, "html5lib")
    contents = get_path_content_func([])(soup, [])
    ctree = []

    for xpath, content in contents:
        for i, path in enumerate(xpath):
            idx = indexer.get_index(path)
            if i == len(ctree):
                ctree.append(set())
            ctree[i].add(idx)
    vector = [0] * len(indexer)
    for deep, i in enumerate(ctree):
        for idx in i:
            vector[idx] += deep + 1
    return vector


def process_domain(domain: str):
    global indexer
    indexer = WordIndexer(key="INDEXER_" + domain)
    client = MongoClient(config.spider_mongo_str)
    coll: Collection = client.spider.extend_raw_doc_2020_04_29
    condense_raw: Collection = client.spider.vector_domain
    craw_metadata = client.spider.vector_domain_metadata
    for doc in coll.find({"domain": domain}):
        r = get_condense_html_tree(doc['html'], doc['url'], doc['domain'])
        condense_raw.insert_one({
            'url': doc['url'],
            'domain':domain,
            'incid': doc['incid'],
            'condense_data': r,
        })

    craw_metadata.update_one({"domain": domain}, {"$set": {
        "domain_dict": indexer.get_dic(),
        "domain_dimension": len(indexer)
    }}, upsert=True)
    del indexer


def process_all_domain():
    client = MongoClient(config.spider_mongo_str)
    dcoll: Collection = client.spider.candidate_domain
    domain_list = list(dcoll.find())
    for cdoc in domain_list:
        domain = cdoc['domain']
        process_domain(domain)


if __name__ == '__main__':
    process_all_domain()
    pass
