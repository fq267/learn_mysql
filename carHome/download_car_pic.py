import datetime

import requests
import random
import time
import os
import re
from pathlib import Path
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from pymongo import MongoClient


followPage = '/pic/series/\d+-\d+-p\d+\.html'


def download_by_requests(url, re_times=3, base_url=''):
    if url.startswith('http'):
        pass
    elif len(base_url) > 0:
        url = urljoin(base_url, url)
    else:
        raise UserWarning("you need base url ,but it is empty")
    print("This link will be downloaded, ", url)
    try:
        res = requests.get(url, timeout=5)
        if res.status_code >= 300:
            raise UserWarning("http code is larger than 300.")
        else:
            print("succeed downloaded")
            return res
    except Exception as e:
        print("open_url_return_str", e)
        if re_times > 0:
            print("retry times %s" % re_times)
            time.sleep(10)
            return download_by_requests(url, re_times - 1)
        else:
            # raise UserWarning("Something bad happened")
            return None


def download_pic(url, re_times=3):
    base_url = "https://car%d.autoimg.cn" % random.choice([1, 2, 3])
    url = url.replace('/t_', '/1024x0_1_q87_')
    url = url[url.find("autoimg")+11:]
    url = urljoin(base_url, url)
    print("This link will be downloaded, ", url)
    try:
        res = requests.get(url, timeout=5)
        if res.status_code >= 300:
            raise UserWarning("http code is larger than 300.")
        else:
            print("succeed downloaded")
            return res
    except Exception as e:
        print("open_url_return_str", e)
        if re_times > 0:
            print("retry times %s" % re_times)
            time.sleep(1)
            return download_pic(url, re_times - 1)
        else:
            # raise UserWarning("Something bad happened")
            return None


def parse_page_by_patten(patten, content):
    return re.findall(patten, content)


def save_links(list_links):
    conn = MongoClient('localhost', 27017)
    db = conn.carhome
    i = 1
    base_url = 'https://car.autohome.com.cn/'
    for url in set(list_links):
        if url.startswith('http'):
            pass
        elif url.count('p1.') > 0:
            continue
        elif len(base_url) > 0:
            url = urljoin(base_url, url)
        print("找到的翻页链接是 ", url)
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
    conn.close()


conn = MongoClient('localhost', 27017)
db = conn.carhome
search_res = db.serieslinks.find().sort("date", 1)  # '1'是顺序，'-1'是倒叙
conn.close()
for dict_ in search_res:
    entryUrl = dict_['link']
    print("entryurl is ", entryUrl)
    r = download_by_requests(entryUrl, re_times=4)   #从一种车型的图片裤进入
    pyquery_object = pq(r.text)
    page_links = parse_page_by_patten(followPage, r.text)   #获取翻页链接
    print("获取到的翻页链接是 ", page_links)
    save_links(page_links)
    name_of_car = pyquery_object.find('.fn-left.cartab-title-name').text()      #获取车型的名字
    print('name_of_car', name_of_car)
    path_dir = 'D:\downloaded_pic\%s\\' % name_of_car       #判断该车型的目录是否存在，不存在就创建
    if not Path(path_dir).exists():
        os.mkdir(path_dir)
    dict_of_kind = {'1': '车身外观', '10': '中控方向盘', '3': '车厢座椅', '12': '其它细节', '51': '改装', '14': '图解'}
    kind = 1    #后面通过链接截取来判断， 或者通过页面获取。
    kind_name = dict_of_kind['1']
    p_num_patt = re.compile('-p(\d+)')  #计算图片的序号
    page_num = p_num_patt.findall(entryUrl)
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if page_num:
        i = (int(page_num[0]) - 1) * 60 + 1
    else:
        i = 1
    for item in pyquery_object(".uibox img"):   #获取该页的所有图片链接。但不包括翻页链接
        link_of_chapter = pq(item).attr("src")
        name_of_chapter = pq(item).attr('title')
        name_of_chapter = name_of_chapter + "-" + kind_name
        pic_name = "%s%s_%s.jpg" % (path_dir, i, name_of_chapter)
        print('path_dir is ', path_dir)
        print('pic_name is ', pic_name)
        content = download_pic(link_of_chapter, re_times=8)
        if content:
            with open(pic_name, 'wb') as file:
                print(i, "pic_name is ", pic_name)
                file.write(content.content)
                time.sleep(random.random())
        else:
            with open('error.log', 'a') as efile:
                content = "error: %s, something wrong with link %s" % (date, link_of_chapter)
                print(content)
                efile.write(content + '\n')
                efile.write(' '*20 + 'The entryUrl is: ' + entryUrl + '\n')
                efile.close()
        i += 1
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print("-"*90)
    db.serieslinks.update_one(filter={'link': entryUrl}, update={'$set': {"date": date}}, upsert=True)
    print("\n", "#"*90)
