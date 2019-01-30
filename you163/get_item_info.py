#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
import random
import re
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from pymongo import MongoClient


# 使用webdriver下载页面
def download_by_webdriver(url, charset='utf-8', proxy=None, user_agent=None):
    # 传入URL，使用浏览器下载后，返回页面。
    print("[download_by_webdriver]: begin download the link %s" % url)
    try:
        # 进入浏览器设置
        options = webdriver.ChromeOptions()
        # 谷歌无头模式
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        # options.add_argument('window-size=1200x600')
        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')
        # 设置代理
        if proxy:
            print("[download_by_webdriver]: use proxy %s" % proxy)
            options.add_argument('proxy-server=' + proxy)
        # 添加头
        if user_agent:
            options.add_argument('user-agent=' + user_agent)
        else:
            options.add_argument(
                'user-agent=' + 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) '
                                'AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/71.0.3578.98 Safari/537.36')
        # 设置驱动服务
        c_service = Service('/usr/local/bin/chromedriver')
        c_service.command_line_args()
        c_service.start()
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(15)
        p_content = driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
        current_url = driver.current_url
        driver.quit()
        c_service.stop()
    except Exception as e:
        print("[download_by_webdriver]:", e)
        p_content, current_url = None, None
    return p_content, current_url


def get_detail_info(page_content, current_link=""):
    # 解析页面，获取商品信息
    pyquery_object = pq(page_content, parser="html")
    print("[get_detail_info]: current link {}".format(current_link))
    # you163
    data_dict = dict()
    try:
        # 判断是否下架，如果下架，就直接返回直包含了名字为"已下架字样"的data_dict
        # removed_item = pyquery_object.find("div.error-notice-hd")
        # if removed_item:
        #     data_dict["name_of_item"] = removed_item.text()
        #     return data_dict

        # 获取严选商品名字
        data_dict["name_of_item"] = get_item_name(pyquery_object)

        # 获取严选商品现价
        data_dict["current_price"] = get_item_current_price(pyquery_object)

        # 获取严选商品原价
        data_dict["origin_price"] = get_item_origin_price(pyquery_object)

        # 获取严选商品评价
        data_dict["attributes_of_item"] = get_item_attr(pyquery_object)

        # 获取严选商品ID
        data_dict["id_of_item"] = get_item_id(current_link)

        # 获取严选商品的主分类ID
        data_dict["category_id"] = get_category_id(pyquery_object)

        # 获取严选商品的子分类ID
        data_dict["sub_category_id"] = get_sub_category_id(pyquery_object)

    except Exception as e:
        print("[get_detail_info]:", data_dict, "\n", e)
        data_dict.clear()
    finally:
        return data_dict


# 获取严选商品ID
def get_item_id(link):
    item_id = None
    # 通过当前链接获取
    item_id = re.search(r"id=(\d+)", link).group(1)
    if item_id:
        print("[item_id]: {}".format(item_id))
    else:
        # print("Failed to get item id.")
        raise UserWarning("Failed to get item id.")
    return item_id


# 获取子种类ID
def get_sub_category_id(pyquery_object):
    # 初始化sub_category_id为None
    sub_category_id = None
    # 导航条获取
    sub_category_id_node = pyquery_object.find('span[data-reactid=".2.0.$2"] a').attr("href")
    if isinstance(sub_category_id_node, str):
        if sub_category_id_node.find("Category"):
            sub_category_id = re.search(r"subCategoryId=(\d+)", sub_category_id_node).group(1)
    # if not store_name:
    #     # 通过一种节点获取
    #     store_name_node = pyquery_object.find('.tb-shop-name a').text()
    #     if isinstance(store_name_node, str):
    #         if len(store_name_node) > 0:
    #             store_name = store_name_node.strip()
    # if not store_name:
    #     # 通过另一种节点获取
    #     store_name_node = pyquery_object.find('.shop-name-wrap a.shop-name-link').text()
    #     if isinstance(store_name_node, str):
    #         if len(store_name_node) > 0:
    #             store_name = store_name_node.strip()
    if sub_category_id:
        print("[category_id]: {}".format(sub_category_id))
    else:
        # print("Failed to get sub_category id.")
        raise UserWarning("Failed to get sub_category id.")
    return sub_category_id


# 获取主种类ID
def get_category_id(pyquery_object):
    # 初始化category_id为None
    category_id = None
    # 导航条获取
    category_id_node = pyquery_object.find('span[data-reactid=".2.0.$1"] a').attr("href")
    if isinstance(category_id_node, str):
        if category_id_node.find("category"):
            category_id = re.search(r"categoryId=(\d+)", category_id_node).group(1)
    # if not store_name:
    #     # 通过一种节点获取
    #     store_name_node = pyquery_object.find('.tb-shop-name a').text()
    #     if isinstance(store_name_node, str):
    #         if len(store_name_node) > 0:
    #             store_name = store_name_node.strip()
    # if not store_name:
    #     # 通过另一种节点获取
    #     store_name_node = pyquery_object.find('.shop-name-wrap a.shop-name-link').text()
    #     if isinstance(store_name_node, str):
    #         if len(store_name_node) > 0:
    #             store_name = store_name_node.strip()
    if category_id:
        print("[category_id]: {}".format(category_id))
    else:
        # print("Failed to get category id.")
        raise UserWarning("Failed to get category id.")
    return category_id


# 获取严选商店的链接
def get_shop_link(pyquery_object):
    # 初始化store_link为None
    store_link = None
    # 通过商店的名字节点获取链接
    store_link_node = pyquery_object.find('.tb-shop-name a').attr('href')
    if isinstance(store_link_node, str):
        if not store_link_node.startswith('https'):
            store_link = urljoin("https:", store_link_node)
        else:
            store_link = store_link_node
    else:
        # 通过另一个商店名字的节点获取链接
        store_link_node = pyquery_object.find('a.shop-name-link').attr('href')
        if isinstance(store_link_node, str):
            if not store_link_node.startswith('https'):
                store_link = urljoin("https:", store_link_node)
            else:
                store_link = store_link_node
    if store_link:
        print("[store_link]: {}".format(store_link))
    else:
        # print("Failed to get store link.")
        raise UserWarning("Failed to get store link.")
    return store_link


# 获取严选描述
def get_item_attr(pyquery_object):
    # 初始化attr为None
    attr = None
    # 获取商品的文字描述
    attributes_of_item = pyquery_object.find('.m-attrList').text()
    # 去掉换行和多余的空格
    if isinstance(attributes_of_item, str):
        if len(attributes_of_item) > 0:
            attr = attributes_of_item.strip()
            attr = re.sub(r"\s+", " ", attr)
    # if not attr:
    #     # 没有文字描述的，获取图片描述
    #     attributes_of_item = pyquery_object.find("").attr('src')
    #     if isinstance(attributes_of_item, str):
    #         attr = attributes_of_item
    #     else:
    #         # 有时候图片被设定不显示
    #         attributes_of_item = pyquery_object.find('').attr(
    #             'src')
    #         if isinstance(attributes_of_item, str):
    #             attr = attributes_of_item
    if attr:
        print("[item_attribute]: {}".format(attr))
    else:
        # print("Failed to get item attribute.")
        raise UserWarning("Failed to get item attribute.")
    return attr


# 获取严选的原价，有些限制了登录才显示，允许为空值
def get_item_origin_price(pyquery_object):
    # 初始化origin_price为None
    origin_price = None
    origin_price_node = pyquery_object.find('.op s span').text()
    if isinstance(origin_price_node, str):
        origin_price = origin_price_node.strip()
    if origin_price:
        print("[origin_price]: {}".format(origin_price))
    else:
        print("Failed to get item origin price.")
    return origin_price


# 获取严选的现价，有些限制了登录才显示，允许为空值
def get_item_current_price(pyquery_object):
    # 初始化current_price为None
    current_price = None
    current_price_node = pyquery_object.find('.rp .num').text()
    if isinstance(current_price_node, str):
        current_price = current_price_node.strip()
    if current_price:
        print("[current_price]: {}".format(current_price))
    else:
        raise UserWarning("Failed to get item current price.")
    return current_price


# 获取严选的名称
def get_item_name(pyquery_object):
    # 初始化item_name为None
    item_name = None
    item_name_node = pyquery_object.find(".intro .name>span").text()
    if isinstance(item_name_node, str):
        if len(item_name_node) > 0:
            item_name = re.sub(r"\s+", " ", item_name_node)
    if not item_name:
        item_name_node = pyquery_object.find("head title").text()
        if isinstance(item_name_node, str):
            if len(item_name_node) > 0:
                item_name = item_name_node.replace(" - 网易严选", "")
    if item_name:
        print("[item_name]: {}".format(item_name))
    else:
        raise UserWarning("Failed to get item item_name.")
    return item_name


'''定义需要访问的非商品的链接'''
visit_patten = [r"//you.163.com/item/list?categoryId=\d+&subCategoryId=\d+",
                r"//you.163.com/item/list?categoryId=\d+"]
'''定义需要的商品链接格式'''
item_patten = [r"//you.163.com/item/detail?id=\d+"]


# 通过正则表达式，寻找所有符合要求的字符
def parse_page_by_patten(patten, content):
    compile_obj = re.compile(patten)
    return compile_obj.findall(content)


# 获取页面上所需的链接
def get_item_links(page_content):
    # 解析页面，获取链接
    link_list = []
    visit_links = []
    item_links = []
    for v_p in visit_patten:
        link_p = parse_page_by_patten(v_p, page_content)
        visit_links += link_p
    for i_p in item_patten:
        link_v = parse_page_by_patten(i_p, page_content)
        item_links += link_v
    link_list += list(set(visit_links) | set(item_links))
    return link_list


# 保存商店和商品的链接
def save_links(url):
    if not url.startswith('http'):
        url = urljoin("http://you.163.com/", url)
    # 保存商品链接
    if url.find("detail") > 0:
        conn = MongoClient('localhost', 27017)
        db = conn.you163
        filter_link = {'link': {'$eq': url}}
        search_res = db.item_info.find_one(filter_link)
        if not search_res:
            d1 = datetime.datetime.now()
            date = d1 - datetime.timedelta(days=25)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            db.item_info.insert_one({"link": url, "data": date})
            print("The current saved link: %s" % url)
        else:
            print("Link %s is exist in the db." % url)
    # 保存非商品链接
    elif url.find("categoryId") > 0:
        conn = MongoClient('localhost', 27017)
        db = conn.you163
        filter_link = {'link': {'$eq': url}}
        search_res = db.store_info.find_one(filter_link)
        if not search_res:
            d1 = datetime.datetime.now()
            date = d1 - datetime.timedelta(days=25)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            db.store_info.insert_one({"link": url, "data": date})
            print("The current saved link: %s" % url)
        else:
            print("Link %s is exist in the db." % url)


# 保存详情
def save_detail_info(link, data):
    conn = MongoClient('localhost', 27017)
    db = conn.you163
    db.item_info.update_one(filter={'link': link}, update={'$set': data}, upsert=True)


# 按照访问时间的顺序排列，获取指定数量的商品链接，并返回列表。
def get_item_link_from_db(num=5):
    conn = MongoClient('localhost', 27017)
    db = conn.you163
    filter_link = {'full_info': {'$ne': "1"}}
    search_res = db.item_info.find(filter_link, limit=num, no_cursor_timeout=True).sort("data", -1)  # '1'是顺序，'-1'是倒叙
    conn.close()
    for dict_ in search_res:
        # 获取商品的链接，并添加到全局变量waiting_link_set中
        link = dict_["link"]
        if not link in LINK_LIST:
            LINK_LIST.append(link)


# 文件操作
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


IP_LIST = file_operate("/Users/fanq/Workspace/learn_mysql/you163/ip.txt", "r")
LINK_LIST = []


def entry():
    while 1:
        # 当待访问链接少于3条时，自动从数据库中获取
        if len(LINK_LIST) <= 3:
            # 每次获取10条
            get_item_link_from_db(250)

        # 获取一个商品链接
        item_link = LINK_LIST.pop()

        # 获取一个代理地址
        proxy_ip = None
        ip = random.choice(IP_LIST)
        if len(ip) > 1:
            proxy_ip = ip

        # 通过webdriver获取页面，以及实际跳转后的链接
        content, c_link = download_by_webdriver(item_link, proxy=None)
        if content:
            # 获取更多商品或者商店链接
            links = get_item_links(content)
            # 保存链接到数据库
            for got_link in links:
                save_links(got_link)
            # 获取商品信息
            info = get_detail_info(content, c_link)
            if isinstance(info.get("name_of_item"), str):
                if len(info.get("name_of_item")) > 0:
                    d1 = datetime.datetime.now()
                    info["full_info"] = "1"
                    info["data"] = d1.strftime('%Y-%m-%d %H:%M:%S')
                    # 保存商品信息
                    save_detail_info(item_link, info)
                    print("[date:]", d1, "got info is ", info)
                else:
                    print("\n", content, "\n")
                    print("[main]: name of item is zero")
            else:
                IP_LIST.remove(proxy_ip)
                print("##########################\n", content, "\n############################")
                print("[main]: type of info is %s" % type(info), info)
                # time.sleep(15)
        if len(LINK_LIST) == 0:
            break
        print("#" * 100)

