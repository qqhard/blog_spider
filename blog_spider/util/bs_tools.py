#!
# __author__ = 'valseek'
# __create_time__ = '2020/5/5 5:10 PM'

import re

from bs4.element import Tag

escape_re = r'([\+.~`@#%&=\'\\:;<>,/\(\)])'
escape_replace = r'\\\1'


def get_new_path(tag: Tag, xpath, add_id=False):
    add_xpath = tag.name
    id = tag.attrs.get("id")
    if id is not None and add_id is True:
        add_xpath += "#" + str.strip(re.sub(escape_re, escape_replace, id))
    clss = tag.attrs.get("class")
    if clss is not None and tag.name != "p":
        for cls in clss:
            add_xpath = add_xpath + "." + str.strip(re.sub(escape_re, escape_replace, cls))
            break
    if add_xpath != "":
        xpath.append(add_xpath)
    return xpath


def get_tag_path(tag: Tag):
    ptag = tag
    path = []
    while ptag is not None and ptag.name != "html":
        path = get_new_path(ptag, path)
        ptag = ptag.parent
    path.reverse()
    return " ".join(path)


