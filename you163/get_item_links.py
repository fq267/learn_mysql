#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
import requests
import re
import random
from urllib.parse import urljoin
from pymongo import MongoClient


def download_by_webdriver(url, charset='utf-8'):
    # 传入URL，使用浏览器下载后，返回页面。
    print("[download_by_webdriver]: begin download the link %s" % url)
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        c_service = Service('/usr/local/bin/chromedriver')
        c_service.command_line_args()
        c_service.start()
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        driver.implicitly_wait(10)
        content = driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
        current_url = driver.current_url
        driver.quit()
        c_service.stop()
    except Exception as e:
        print("[download_by_webdriver]:", e)
        content, current_url = None, None
    return content, current_url


def download_by_requests(url, re_times=3, base_url='http:'):
    if url.startswith('http'):
        pass
    elif len(base_url) > 0:
        url = urljoin(base_url, url)
    else:
        raise UserWarning("you need base url ,but it is empty")
    print("[download_by_requests]: begin download the link %s" % url)
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
            return download_by_requests(url, re_times - 1)
        else:
            # raise UserWarning("Something bad happened")
            return None


# 通过requests获取所有大分类的id，并且组合成链接。
def get_all_category_id(page_content):
    all_id = re.findall(r"categoryId=(\d+)", page_content)
    all_id = set(all_id)
    if len(all_id) > 0:
        links = ["http://you.163.com/item/list?categoryId=%s" % x for x in all_id]
    else:
        raise UserWarning("[get_all_category_id]: Failed to get categoryId")
    return links


# 通过webdriver获取每个大类下面的所有商品。
def get_items_link(url):
    content, current_url = download_by_webdriver(url)
    all_links = re.findall(r"/item/detail\?id=\d+", content)
    all_links = list(set(all_links))
    return [urljoin("http://you.163.com/", x) for x in all_links]


# 保存商品链接到数据库。
def save_links(data_dict):
    # 链接处理
    # if not url.startswith('https'):
    #     url = urljoin("https:", url)
    # 保存商品链接
    # 必须包含第一个链接，即必须有link的值
    item_normal_link = data_dict.get("link")
    if item_normal_link:
        conn = MongoClient('localhost', 27017)
        db = conn.you163
        filter_link = {'link': {'$eq': item_normal_link}}
        search_res = db.item_info.find_one(filter_link)
        # 判断该链接是否已经存在于数据库，是就打印消息，否就存入。
        if not search_res:
            d1 = datetime.datetime.now()
            date = d1 - datetime.timedelta(days=30)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            data_dict["data"] = date
            db.item_info.insert_one(data_dict)
            print("{}: The current saved link: {}".format(d1, item_normal_link))
        else:
            print("Link {} is exist in the db.".format(item_normal_link))


def entry():
    home_url = "http://you.163.com/item/list?categoryId=1005000"
    home_page = download_by_requests(home_url)
    all_category_links = get_all_category_id(home_page.text)
    for category_link in all_category_links:
        print("#" * 120)
        item_links = get_items_link(category_link)
        time.sleep(random.randint(2, 10))
        for item_link in item_links:
            data_dict = dict()
            data_dict["link"] = item_link
            data_dict["full_info"] = 0
            save_links(data_dict)


if __name__ == '__main__':
    entry()
