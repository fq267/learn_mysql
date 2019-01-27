#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from selenium import webdriver
import time
import re
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from pymongo import MongoClient

waiting_link_list = []


def download_by_webdrive(url, charset='gbk'):
    # 传入URL，使用浏览器下载后，返回页面。
    print("[download_by_webdrive]: begin download the link %s" % url)
    try:
        driver = webdriver.Chrome()
        # driver = webdriver.PhantomJS()
        driver.get(url)
        driver.implicitly_wait(10)
        content = driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
        driver.quit()
    except Exception as e:
        print("[download_by_webdrive]:", e)
        content = None
    return content


def get_detail_info(page_content, current_link=""):
    # 解析页面，获取商品信息
    pyquery_object = pq(page_content, parser="html")
    # taobao_site = pyquery_object.find('div.site-nav-menu-hd')
    # tmall_site = pyquery_object.find('p.sn-back-home')
    print("[get_detail_info]: current_link", current_link)
    # taobao
    data_dict = dict()
    if current_link.find("taobao") > 0:
        print("[get_detail_info]: taobao item")
        try:
            name_of_item = pyquery_object.find('#J_Title .tb-main-title').text()
            data_dict["name_of_item"] = re.sub("\s+", " ", name_of_item)
            # 有些商品需要登录查看现价
            data_dict["current_price"] = pyquery_object.find('#J_PromoPriceNum').text().strip()
            data_dict["origin_price"] = pyquery_object.find('#J_StrPrice').text().strip()
            data_dict["rate_counter"] = pyquery_object.find('#J_RateCounter').text().strip()
            data_dict["sell_counter"] = pyquery_object.find('#J_SellCounter').text().strip()
            attributes_of_item = pyquery_object.find('.attributes-list').text().strip()
            # 去掉换行和多余的空格
            data_dict["attributes_of_item"] = re.sub("\s+", " ", attributes_of_item)
            item_and_shop_id = pyquery_object.find('.tb-main-pic a').attr('href')
            # item_and_shop_id = pyquery_object.find('.tb-gallery .tb-main-pic a').attr('href')
            item_and_shop_id_obj = re.search("itemId=(\d+).+shopId=(\d+)", item_and_shop_id)
            if item_and_shop_id_obj:
                data_dict["id_of_item"] = item_and_shop_id_obj.group(1)
                data_dict["id_of_store"] = item_and_shop_id_obj.group(2)
            data_dict["name_of_store"] = pyquery_object.find('.tb-shop-name a').text().strip()
            link_of_store = pyquery_object.find('.tb-shop-name a').attr('href')
            if not link_of_store:
                link_of_store = pyquery_object.find('a.shop-name-link').attr('href')
                data_dict["name_of_store"] = pyquery_object.find('.tb-shop-name a').text().strip()
            if isinstance(link_of_store, str):
                if not link_of_store.startswith('https'):
                    link_of_store = urljoin("https:", link_of_store)
            data_dict["link_of_store"] = link_of_store
        except Exception as e:
            print("[get_detail_info]:", data_dict, "\n", e)
            print("[get_detail_info]: cannot find item and shop id", "\n", page_content)
            data_dict.clear()
        finally:
            return data_dict
    # tmall
    elif current_link.find("tmall") > 0:
        print("[get_detail_info]: tmall item")
        try:
            name_of_item = pyquery_object.find('div.tb-detail-hd').text()
            data_dict["name_of_item"] = re.sub("\s+", " ", name_of_item)
            data_dict["current_price"] = pyquery_object.find('#J_StrPriceModBox .tm-price').text().strip()
            data_dict["origin_price"] = pyquery_object.find('#J_PromoPrice .tm-price').text().strip()
            data_dict["rate_counter"] = pyquery_object.find('.tm-ind-sellCount .tm-count').text().strip()
            data_dict["sell_counter"] = pyquery_object.find('.tm-ind-reviewCount .tm-count').text().strip()
            attributes_of_item = pyquery_object.find('#J_AttrUL li').text().strip()
            # 去掉换行和多余的空格
            data_dict["attributes_of_item"] = re.sub("\s+", " ", attributes_of_item)
            # item_and_shop_id = pyquery_object.find('.tb-gallery .tb-main-pic a').attr('href')
            # item_and_shop_id_obj = re.search("itemId=(\d+).+shopId=(\d+)", item_and_shop_id)
            # if item_and_shop_id_obj:
            #     data_dict["id_of_item"] = item_and_shop_id_obj.group(1)
            #     data_dict["id_of_store"] = item_and_shop_id_obj.group(2)
            data_dict["id_of_item"] = pyquery_object.find('#LineZing').attr('shopid')
            data_dict["id_of_store"] = pyquery_object.find('#LineZing').attr('itemid')
            # 获取商店名称
            data_dict["name_of_store"] = pyquery_object.find('.shop-name a').text().strip()
            # 获取商店链接
            link_of_store = pyquery_object.find('.tb-shop-name a').attr('href')
            link_of_store1 = pyquery_object.find('meta[name="microscope-data"]').attr('content')
            if link_of_store:
                data_dict["link_of_store"] = link_of_store
            elif len(data_dict.get("id_of_store")) > 5:
                link_of_store = "https://shop%s.taobao.com" % data_dict.get("id_of_store")
                data_dict["link_of_store"] = link_of_store
            elif len(link_of_store1) > 10:
                id_of_store = re.search("shopId=(\d+)", link_of_store1).group(1)
                link_of_store = "https://shop%s.taobao.com" % id_of_store
                data_dict["link_of_store"] = link_of_store
                data_dict["id_of_store"] = id_of_store
        except Exception as e:
            print(data_dict, "\n", e)
            print("cannot find item and shop id", "\n", page_content)
            data_dict.clear()
        finally:
            return data_dict
    else:
        print("[get_detail_info]: not taobao tmall. current_link is %s" % current_link)
        return data_dict


'''定义需要访问的非商品的链接'''
# https://jupage.taobao.com/wow/tttj/act/index
visit_patten = ["//shop\d+.taobao.com", "//[a-z-A-Z.]{3,20}.taobao.com", "//[a-z-A-Z.]{3,20}.tmall.com",
                "//jupage.taobao.com/\w+/\w+/\w+/index"]
'''定义需要的商品链接格式'''
item_patten = ["//detail.tmall.com/item.htm[0-9-a-z_A-Z.?&=]+id=\d+",
               "/item.taobao.com/item.htm[0-9-a-z_A-Z.?&=]+id=\d+"]


def parse_page_by_patten(patten, content):
    compile_obj = re.compile(patten)
    return compile_obj.findall(content)


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


def save_links(url):
    if not url.startswith('https'):
        url = urljoin("https:", url)
    # 保存商品链接
    if url.find("item.htm") > 0:
        conn = MongoClient('localhost', 27017)
        db = conn.taobao_spider
        filter_link = {'link': {'$eq': url}}
        search_res = db.item_info.find_one(filter_link)
        if not search_res:
            d1 = datetime.datetime.now()
            date = d1 - datetime.timedelta(days=5)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            db.item_info.insert_one({"link": url, "date": date})
            print("The current saved link: %s" % url)
        else:
            print("Link %s is exist in the db." % url)
    # 保存非商品链接
    elif url.find("/shop") > 0:
        conn = MongoClient('localhost', 27017)
        db = conn.taobao_spider
        filter_link = {'link': {'$eq': url}}
        search_res = db.store_info.find_one(filter_link)
        if not search_res:
            d1 = datetime.datetime.now()
            date = d1 - datetime.timedelta(days=2)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            db.store_info.insert_one({"link": url, "date": date})
            print("The current saved link: %s" % url)
        else:
            print("Link %s is exist in the db." % url)


def save_detail_info(link, data):
    # 保存详情
    conn = MongoClient('localhost', 27017)
    db = conn.taobao_spider
    db.item_info.update_one(filter={'link': link}, update={'$set': data}, upsert=True)


def get_item_link_from_db(num=5):
    # 按照访问时间的顺序排列，获取指定数量的商品链接，并返回列表。
    conn = MongoClient('localhost', 27017)
    db = conn.taobao_spider
    filter_link = {'visited': {'$ne': "1"}}
    search_res = db.item_info.find(filter_link, limit=num, no_cursor_timeout=True).sort("date", 1)  # '1'是顺序，'-1'是倒叙
    conn.close()
    for dict_ in search_res:
        # 获取商品的链接，并添加到全局变量waiting_link_set中
        link = dict_["link"]
        if not link in waiting_link_list:
            waiting_link_list.append(link)


while 1:
    # 当待访问链接少于3条时，自动从数据库中获取
    if len(waiting_link_list) <= 33:
        # 每次获取10条
        get_item_link_from_db(40)
    # 访问链接
    item_link = waiting_link_list.pop()
    # item_link = "https://detail.tmall.com/item.htm?id=574052830642"
    # 通过webdriver获取页面
    page_content = download_by_webdrive(item_link)
    if page_content:
        # print(page_content)
        # 获取更多商品或者商店链接
        # links = get_item_links(page_content)
        # 保存链接到数据库
        # for got_link in links:
        #     save_links(got_link)
        # 获取商品信息
        info = get_detail_info(page_content, item_link)
        if isinstance(info.get("name_of_item"), str):
            if len(info.get("name_of_item")) > 0:
                info["visited"] = "1"
                # 保存商品信息
                save_detail_info(item_link, info)
                d1 = datetime.datetime.now()
                print("[date:]", d1, "got info is ", info)
            else:
                print("\n", page_content, "\n")
                print("[main]: name of item is zero")
        else:
            print("\n", page_content, "\n")
            print("[main]: type of info is %s" % type(info), info)
    print("#" * 100)

# with open("item2.html", "r", encoding='gbk') as f:
#     page_content = f.read()
# current_link = "https://detail.tmall.com/item.htm?id=574052830642"
# print(get_detail_info(page_content, current_link))
