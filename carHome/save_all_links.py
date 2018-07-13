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
brandLinks = parse_page_by_patten(str_home, pattenbrand)
seriesLinks = parse_page_by_patten(str_home, pattenseries)
for link in brandLinks:
    time.sleep(random.randint(1, 5))
    str_brand = download_by_requests(link, re_times=5, base_url='https://car.autohome.com.cn/')
    print('seriesLinks is: ', len(seriesLinks))
    seriesLinks += parse_page_by_patten(str_brand, pattenseries)

conn = MongoClient('localhost', 27017)
db = conn.carhome
i = 1
base_url = 'https://car.autohome.com.cn/'
for url in set(seriesLinks):
    if url.startswith('http'):
        pass
    elif len(base_url) > 0:
        url = urljoin(base_url, url)
    url = url.replace('.html', '-1-p1.html')
    filter_link = {'link': {'$eq': url}}
    search_res = db.serieslinks.find_one(filter_link)
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    if not search_res:
        db.serieslinks.insert_one({"link": url, "date": date})
        print("%d links have added into database" % i, "the info as following: ")
        print(url, date)
        i += 1
    else:
        print("This link is existed, link is %s" % url)
    print('#'*80, '\n')
    i += 1
conn.close()

# https://car.autohome.com.cn/pic/series/3126-1-p2.html