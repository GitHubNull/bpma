#-*-coding:utf-8-*-
import lxml.html.soupparser as soupparser
import requests
headers = {
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
}
def get_domtree(html):
    dom = soupparser.fromstring(html)
    for child in dom.iter():
        yield child.tag

def similar_web(a_url,b_url):
    html1 = requests.get(a_url,headers=headers).text
    html2 = requests.get(b_url,headers=headers).text
    dom_tree1 = ">".join(list(filter(lambda e: isinstance(e,str),list(get_domtree(html1)))))
    dom_tree2 = ">".join(list(filter(lambda e: isinstance(e,str),list(get_domtree(html2)))))
    c,flag,length = lcs(dom_tree1,dom_tree2)
    return 2.0*length/(len(dom_tree1)+len(dom_tree2))

percent = similar_web(
'http://edmondfrank.github.io/blog/2017/04/05/qian-tan-mongodb/',
'http://edmondfrank.github.io/blog/2017/03/27/emacsshi-yong-zhi-nan/')
print(percent) #相似度（百分比）
