#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import requests
import random
import re
from pymongo import MongoClient
from pyquery import PyQuery as pq
from urllib.parse import urljoin

proxy_ip = []


def download_by_requests(url, re_times=3):
    # if url.startswith('http'):
    #     pass
    # elif len(base_url) > 0:
    #     url = urljoin(base_url, url)
    # else:
    #     raise UserWarning("you need base url ,but it is empty")
    print("This link will be downloaded, ", url)
    # proxy = random.choice(proxy_ip)
    # print("Use proxy %s" % proxy)
    try:
        res = requests.get(url, timeout=5)
        # res = requests.get('https://www.example.com', timeout=5, proxies={"http": "http://{}".format(proxy)})
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
            # proxy_ip.remove(proxy)
            pass


def get_proxy():
    with open("/Users/fanq/Workspace/learn_mysql/taobao/ip.txt", "r") as f:
        return f.readlines()


def get_detail_info(page_content, url):
    # 解析页面，获取商品信息
    # print(page_content)
    data_dict = dict()
    data_dict["link_of_item3"] = url
    pyquery_object = pq(page_content)
    head_links = pyquery_object("head link")
    for link_html_obj in head_links:
        py_query_py_query = pq(link_html_obj)
        if py_query_py_query.attr("rel") == "canonical":
            # https://detail.tmall.com/item.htm?id=10710811953
            data_dict["link"] = py_query_py_query.attr("href")
        elif py_query_py_query.attr("rel") == "amphtml":
            # https://www.taobao.com/list/item-amp/10710811953.htm
            # https://www.taobao.com/list/item-amp/583872706305.htm
            data_dict["link_of_item1"] = py_query_py_query.attr("href")
        elif py_query_py_query.attr("rel") == "alternate":
            # https://world.taobao.com/item/10710811953.htm
            data_dict["link_of_item2"] = py_query_py_query.attr("href")
    return data_dict


def save_links(data_dict):
    # 链接处理
    # if not url.startswith('https'):
    #     url = urljoin("https:", url)
    # 保存商品链接
    # 必须包含第一个链接，即必须有link_of_item的值
    item_normal_link = data_dict.get("link")
    print(item_normal_link)
    if item_normal_link:
        conn = MongoClient('localhost', 27017)
        db = conn.taobao_spider
        filter_link = {'link': {'$eq': item_normal_link}}
        search_res = db.item_info.find_one(filter_link)
        if not search_res:
            d1 = datetime.datetime.now()
            date = d1 - datetime.timedelta(days=5)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            data_dict["data"] = date
            db.item_info.insert_one(data_dict)
            print("The current saved link: %s" % item_normal_link)
        else:
            print("Link %s is exist in the db." % item_normal_link)


import threading


def entry(key_word):
    base_url = "https://re.taobao.com/search?keyword="
    for i in range(1, 50):
        url = base_url + str(key_word).strip() + "&_input_charset=utf-8&page=" + str(i)
        re_page = download_by_requests(url).text
        # print(re_page)
        pq_obj = pq(re_page)
        links_and_names_obj = pq_obj.find("#J_waterfallWrapper .item a")
        for link_obj in links_and_names_obj:
            link_of_item3 = pq(link_obj).attr("href")
            item_page = download_by_requests(link_of_item3).text
            data = get_detail_info(item_page, link_of_item3)
            save_links(data)


def get_key_words_in_file():
    with open("/Users/fanq/Workspace/learn_mysql/taobao/hot_keys", "r", encoding="utf-8") as f:
        return f.readlines()


if __name__ == '__main__':
    # proxy_ip = get_proxy()
    key_word = random.choice(get_key_words_in_file())
    entry(key_word)
