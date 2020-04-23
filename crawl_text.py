
import sys


from bs4 import BeautifulSoup, Comment
from bs4.element import Tag


def cal_node_dense(node):
    tag_num = 0.0
    char_num = 0.0
    sum_dense = 0.0
    max_dense = 0.0
    max_node = None

    if isinstance(node, Tag):
        for son in node.children:
            s_tag_num, s_char_num, s_max_dense, s_max_node = cal_node_dense(son)
            tag_num += s_tag_num + 1
            char_num += s_char_num
            sum_dense += s_char_num / max(1.0, s_tag_num)
            if s_max_dense > max_dense:
                max_dense = s_max_dense
                max_node = s_max_node
        if sum_dense > max_dense:
            max_dense = sum_dense
            max_node = node
    else:
        return 0, len(node.string), len(node.string) / 1.0, node

    if sum_dense >= 100:
        print(round(sum_dense, 2), tag_num, char_num, node.name, node.attrs)

    return tag_num, char_num, max_dense, max_node


html = ''

while True:
    line=sys.stdin.readline()
    if line == '':
        break
    html += line

soup = BeautifulSoup(html)
body = soup.body

for o in body.find_all(['script','style','a']):
    o.decompose()

for o in body.findAll(text=lambda text: isinstance(text, Comment)):
    o.extract()



_,_,max_dense,max_node = cal_node_dense(body)
print(max_node.name, max_node.attrs)
r
