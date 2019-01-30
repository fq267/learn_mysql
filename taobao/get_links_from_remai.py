#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import requests
import random
import time
from pymongo import MongoClient
from pyquery import PyQuery as pq

# 全局变量，包含所有的代理IP
PROXY_IP_LIST = []
# 包含了访问过的热词
VISITED_HOT_KEYS = "/Users/fanq/Workspace/learn_mysql/taobao/visited_hot_keys"
# 包含了所有希望被访问的热词
ALL_HOT_KEYS = "/Users/fanq/Workspace/learn_mysql/taobao/hot_keys"
# 包含了所有可用的代理IP
PROXY_IP_FILE = "/Users/fanq/Workspace/learn_mysql/taobao/ip.txt"
# 热词搜索页面可以翻页，下面定义起止页数
FROM_PAGE = 1
END_PAGE = 10


def download_by_requests(url, re_times=2):
    print("This link will be downloaded, ", url)
    # 随机获取一个代理ip
    proxy = random.choice(PROXY_IP_LIST)
    print("Use proxy {}".format(proxy))
    proxies = {"http": "http://{}".format(proxy)}
    headers = {
        "User_Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
    try:
        res = requests.get(url=url, headers=headers, proxies=proxies, timeout=30)
        if not res.status_code == 200:
            raise UserWarning("Failed to download this page.")
        else:
            return res
    except Exception as e:
        print("[download_by_requests]: ", e)
        if re_times > 0:
            print("retry times {}".format(re_times))
            return download_by_requests(url, re_times - 1)
        else:
            PROXY_IP_LIST.remove(proxy)
            return None


def get_proxy():
    return file_operate(PROXY_IP_FILE, "r")


def get_detail_info(page_content, url):
    # 解析页面，获取商品信息
    data_dict = dict()
    data_dict["link_of_item3"] = url
    pyquery_object = pq(page_content)
    # 从head里面获取商品的三种链接
    head_links = pyquery_object("head link")
    for link_html_obj in head_links:
        py_query_py_query = pq(link_html_obj)
        if py_query_py_query.attr("rel") == "canonical":
            # 示例：https://detail.tmall.com/item.htm?id=10710811953
            data_dict["link"] = py_query_py_query.attr("href")
        elif py_query_py_query.attr("rel") == "amphtml":
            # 示例：https://www.taobao.com/list/item-amp/10710811953.htm
            data_dict["link_of_item1"] = py_query_py_query.attr("href")
        elif py_query_py_query.attr("rel") == "alternate":
            # 示例：https://world.taobao.com/item/10710811953.htm
            data_dict["link_of_item2"] = py_query_py_query.attr("href")
    return data_dict


def save_links(data_dict):
    # 链接处理
    # if not url.startswith('https'):
    #     url = urljoin("https:", url)
    # 保存商品链接
    # 必须包含第一个链接，即必须有link的值
    item_normal_link = data_dict.get("link")
    print(item_normal_link)
    if item_normal_link:
        conn = MongoClient('localhost', 27017)
        db = conn.taobao_spider
        filter_link = {'link': {'$eq': item_normal_link}}
        search_res = db.item_info.find_one(filter_link)
        # 判断该链接是否已经存在于数据库，是就打印消息，否就存入。
        if not search_res:
            d1 = datetime.datetime.now()
            date = d1 - datetime.timedelta(days=5)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            data_dict["data"] = date
            db.item_info.insert_one(data_dict)
            print("{}: The current saved link: {}".format(d1, item_normal_link))
        else:
            print("Link {} is exist in the db.".format(item_normal_link))


def entry(key_word):
    base_url = "https://re.taobao.com/search?keyword="
    for page_num in range(FROM_PAGE, END_PAGE):
        url = base_url + str(key_word).strip() + "&_input_charset=utf-8&page=" + str(page_num)
        re_page = download_by_requests(url)
        if not re_page:
            time.sleep(5)
            continue
        pq_obj = pq(re_page.text)
        # 获取搜索页面的所有商品节点
        links_and_names_obj = pq_obj.find("#J_waterfallWrapper .item a")
        for link_obj in links_and_names_obj:
            # 遍历所有节点，获取每个节点的商品链接，再次爬取，获取更多商品信息。
            link_of_item3 = pq(link_obj).attr("href")
            download_obj = download_by_requests(link_of_item3)
            time.sleep(random.randint(1, 6))
            if download_obj:
                item_page = download_obj.text
                data = get_detail_info(item_page, link_of_item3)
                save_links(data)
            else:
                continue


def file_operate(path, mode="r", content=None, encoding="utf-8"):
    if mode == "r" or mode == "read":
        with open(path, mode, encoding=encoding) as f:
            lines = f.readlines()
        f.close()
        return lines
    elif mode == "w" or mode == "write":
        with open(path, mode, encoding=encoding) as f:
            for link in content:
                f.write(link + "\n")
        f.close()
        return None
    elif mode == "a" or mode == "append":
        with open(path, mode, encoding=encoding) as f:
            f.write(content)
        f.close()
        return None


if __name__ == '__main__':
    # proxy_ip是一个全局的列表，包含了所有的代理ip。
    PROXY_IP_LIST = get_proxy()
    # 获取所有的热词
    wait_list = file_operate(ALL_HOT_KEYS, mode="r")
    while len(PROXY_IP_LIST) > 0:
        time.sleep(0.1)
        # 读取已经搜过的关键词
        visited_list = file_operate(VISITED_HOT_KEYS, "r")
        # 将所有的热词减去已经搜索过的，得到需要执行的热词列表
        list_keys = ret_list = list(set(wait_list) - set(visited_list))
        #  当没有热词时停下
        if len(list_keys) <= 0:
            print("All hot key have been visited.")
            break
        #  随机选取1个热词执行搜索
        word = random.choice(list_keys)
        print("#" * 100)
        print("[word] is {}".format(word))
        try:
            entry(word)
        except Exception as e:
            word = None
        finally:
            if word:
                file_operate(VISITED_HOT_KEYS, "a", content=word + "\n")
