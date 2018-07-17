import datetime
import re
import time
import random

import requests
from selenium import webdriver
from urllib.parse import urljoin
from pymongo import MongoClient

'''定义抓取入口，两种需要匹配的链接'''
homepage = "https://car.autohome.com.cn/pic/"
pattenbrand = "/pic/brand-\d+.html"
pattenseries = "/pic/series/\d+.html"
pattenparty = "/pic/series/\d+-\d+.html"


def download_by_phantom(url, charset='gbk'):
    '''return page content as string '''
    browser = webdriver.PhantomJS()
    browser.get(url)
    content = browser.page_source.encode(charset, "ignore").decode(charset, 'ignore')
    return content


def download_by_requests(url, re_times=3, base_url=''):
    if url.startswith('http'):
        pass
    elif len(base_url) > 0:
        url = urljoin(base_url, url)
    else:
        raise UserWarning("you need base url ,but it is empty")
    try:
        res = requests.get(url, timeout=5)
        result_of_download = res.text.encode('gbk', 'ignore').decode('gbk', 'ignore')
        print("succeed downloaded")
        return result_of_download
    except Exception as e:
        print("open_url_return_str", e)
        if re_times > 0:
            print("retry times %s" % re_times)
            time.sleep(10)
            return download_by_requests(url, re_times - 1)
        else:
            raise UserWarning("Something bad happened")


def parse_page_by_patten(patten, content):
    return re.findall(patten, content)


'''获取brand链接'''
str_home = download_by_phantom(homepage)
brandLinks = parse_page_by_patten(pattenbrand, str_home)
seriesLinks = parse_page_by_patten(pattenseries, str_home)
for link in brandLinks:
    str_brand = download_by_requests(link, re_times=5, base_url='https://car.autohome.com.cn/')
    seriesLinks += parse_page_by_patten(pattenseries, str_brand)
seriesLinks = list(set(seriesLinks))
partyLinks = []
k = 1
for link in seriesLinks:
    print('link is ', link)
    print('%s / %s' % (k, len(seriesLinks)))
    str_brand = download_by_requests(link, re_times=5, base_url='https://car.autohome.com.cn/')
    print('partyLinks is: ', len(partyLinks))
    for l in parse_page_by_patten(pattenparty, str_brand):
        if not l in partyLinks:
            partyLinks.append(l)
    k += 1

conn = MongoClient('localhost', 27017)
db = conn.carhome
i = 1
base_url = 'https://car.autohome.com.cn/'
for url in set(partyLinks):
    if url.startswith('http'):
        pass
    elif len(base_url) > 0:
        url = urljoin(base_url, url)
    # url = url.replace('.html', '-1-p1.html')
    filter_link = {'link': {'$eq': url}}
    search_res = db.serieslinks.find_one(filter_link)
    d1 = datetime.datetime.now()
    date = d1 - datetime.timedelta(days=10)
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    if not search_res:
        db.serieslinks.insert_one({"link": url, "date": date})
        print("%d links have added into database" % i, "the info as following: ")
        print(url, date)
        i += 1
    else:
        print("This link is existed, link is %s" % url)
    print('url is ', url)
    time.sleep(1)
    print('#' * 80, '\n')
    i += 1
conn.close()

# https://car.autohome.com.cn/pic/series/3126-1-p2.html
