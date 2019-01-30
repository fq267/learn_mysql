#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from selenium.webdriver.chrome.service import Service
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
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        c_service = Service('/usr/local/bin/chromedriver')
        c_service.command_line_args()
        c_service.start()
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(10)
        content = driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
        current_url = driver.current_url
        driver.quit()
        c_service.stop()
    except Exception as e:
        print("[download_by_webdrive]:", e)
        content = None
    return (content, current_url)


def get_detail_info(page_content, current_link=""):
    # 解析页面，获取商品信息
    pyquery_object = pq(page_content, parser="html")
    print("[get_detail_info]: current link {}".format(current_link))
    # taobao
    data_dict = dict()
    if current_link.find("taobao") > 0:
        print("[get_detail_info]: This is taobao item")
        try:
            # 判断是否下架，如果下架，就直接返回直包含了名字为"已下架字样"的data_dict
            removed_item = pyquery_object.find("div.error-notice-hd")
            if removed_item:
                data_dict["name_of_item"] = removed_item.text()
                return data_dict

            # 获取淘宝商品的名字
            data_dict["name_of_item"] = get_taobao_item_name(pyquery_object)

            # 获取淘宝商品现价
            data_dict["current_price"] = get_taobao_item_current_price(pyquery_object)

            # 获取淘宝商品原价
            data_dict["origin_price"] = get_taobao_item_origin_price(pyquery_object)

            # 获取淘宝商品的评价数量
            data_dict["rate_counter"] = get_taobao_item_rate_num(pyquery_object)

            # 获取淘宝商品的销量
            data_dict["sell_counter"] = get_taobao_item_sell_num(pyquery_object)

            # 获取淘宝商品评价
            data_dict["attributes_of_item"] = get_taobao_item_attr(pyquery_object)

            # 获取淘宝的商品ID
            data_dict["id_of_item"] = get_taobao_item_id(pyquery_object)

            # 获取淘宝商店的ID
            data_dict["id_of_store"] = get_taobao_shop_id(pyquery_object)

            # 获取淘宝商店的名字
            data_dict["name_of_store"] = get_taobao_shop_name(pyquery_object)

            # 获取淘宝商店的链接
            data_dict["link_of_store"] = get_taobao_shop_link(pyquery_object)

        except Exception as e:
            print("[get_detail_info]:", data_dict, "\n", e)
            data_dict.clear()
        finally:
            return data_dict
    # tmall
    elif current_link.find("tmall") > 0:
        print("[get_detail_info]: This is tmall item")
        try:
            # 判断是否下架，如果下架，就直接返回直包含了名字为"已下架字样"的data_dict
            removed_item = pyquery_object.find("div.error-notice-hd")
            if removed_item:
                data_dict["name_of_item"] = removed_item.text()
                return data_dict
            else:
                # 判断商品是否找不到了
                error_page = pyquery_object.find("div.errorDetail h2")
                if error_page:
                    data_dict["name_of_item"] = error_page.text()
                    return data_dict

            # 获取商品的名字
            data_dict["name_of_item"] = get_tmall_item_name(pyquery_object)

            # 获取商品的当前价格
            data_dict["current_price"] = get_tmall_item_current_price(pyquery_object)

            # 获取商品的原价
            data_dict["origin_price"] = get_tmall_item_origin_price(pyquery_object)

            # 获取商品的评论数
            data_dict["rate_counter"] = get_tmall_item_rate_num(pyquery_object)

            # 获取商品的销量
            data_dict["sell_counter"] = get_tmall_item_sell_num(pyquery_object)

            # 获取商品的详情
            data_dict["attributes_of_item"] = get_tmall_item_attr(pyquery_object)

            # 获取商品的ID
            data_dict["id_of_item"] = get_tmall_item_id(pyquery_object)

            # 获取商店的ID
            data_dict["id_of_store"] = get_tmall_store_id(pyquery_object)

            # 获取商店名称
            data_dict["name_of_store"] = get_tmall_store_name(pyquery_object)

            # 获取商店链接
            data_dict["link_of_store"] = get_tmall_store_link(pyquery_object)

        except Exception as e:
            print(data_dict, "\n", e)
            data_dict.clear()
        finally:
            return data_dict
    else:
        print("[get_detail_info]: not taobao tmall. current_link is %s" % current_link)
        return data_dict


def get_tmall_store_link(pyquery_object):
    # 初始化
    store_link = None
    # 第一种方案
    store_link_node = pyquery_object.find('.tb-shop-name a').attr("href")
    if isinstance(store_link_node, str):
        store_link = store_link_node.strip()
    else:
        # 第二种方案
        store_link_node = pyquery_object.find('a.slogo-shopname').attr("href")
        if isinstance(store_link_node, str):
            store_link = store_link_node.strip()
            if not store_link.startswith('https'):
                store_link = urljoin("https:", store_link)
        else:  # 第三种方案
            store_link_node = pyquery_object.find('meta[name="microscope-data"]').attr('content')
            if isinstance(store_link_node, str):
                store_id = re.search("shopId=(\d+)", store_link_node).group(1)
                if store_id:
                    store_link = "https://shop{}.taobao.com".format(store_id)
    if store_link:
        print("[store_link]: {}".format(store_link))
    else:
        # print("Failed to get item id.")
        raise UserWarning("Failed to get store link.")
    return store_link


# 获取天猫商店的名称
def get_tmall_store_name(pyquery_object):
    # 初始化
    store_name = None
    # 第一中方案
    store_name_node = pyquery_object.find('.shop-name a').text()
    if isinstance(store_name_node, str):
        store_name = store_name_node.strip()
        if len(store_name) > 0:
            pass
        else:
            store_name_node = pyquery_object.find('a.slogo-shopname strong').text()
            if isinstance(store_name_node, str):
                if len(store_name_node) > 0:
                    store_name = store_name_node.strip()
    if not store_name:
        store_name_node = pyquery_object.find('input[name="seller_nickname"]').attr("value")
        if isinstance(store_name_node, str):
            store_name = store_name_node.strip()
    if store_name:
        print("[store_name]: {}".format(store_name))
    else:
        # print("Failed to get item id.")
        raise UserWarning("Failed to get store name.")
    return store_name


# 获取天猫商店的ID
def get_tmall_store_id(pyquery_object):
    # 初始化
    store_id = None
    # 第一种方案
    store_id_node = pyquery_object.find('#LineZing').attr('shopid')
    if isinstance(store_id_node, str):
        store_id = store_id_node
    else:
        # 第二种方案
        store_id_node = pyquery_object.find('meta[name="microscope-data"]').attr('content')
        if isinstance(store_id_node, str):
            store_id = re.search("shopId=(\d+)", store_id_node).group(1)
    if store_id:
        print("[store_id]: {}".format(store_id))
    else:
        # print("Failed to get item id.")
        raise UserWarning("Failed to get store id.")
    return store_id


# 获取天猫商品的ID
def get_tmall_item_id(pyquery_object):
    # 初始化
    item_id = None
    item_id_node = pyquery_object.find('#LineZing').attr('itemid')
    if isinstance(item_id_node, str):
        item_id = item_id_node
    else:
        item_id_node = pyquery_object.find('.tb-gallery .tb-main-pic a').attr('href')
        if isinstance(item_id_node, str):
            item_id_re = re.search("itemId=(\d+)", item_id_node)
            item_id = item_id_re.group(1)
    if item_id:
        print("[item_id]: {}".format(item_id))
    else:
        # print("Failed to get item id.")
        raise UserWarning("Failed to get item id.")
    return item_id


def get_tmall_item_attr(pyquery_object):
    # 初始化attr为None
    attr = None
    attributes_of_item = pyquery_object.find('#J_AttrUL li').text()
    # 去掉换行和多余的空格
    if isinstance(attributes_of_item, str):
        if len(attributes_of_item) > 0:
            attr = attributes_of_item.strip()
            attr = re.sub("\s+", " ", attr)
    if not attr:
        # 没有文字描述的，获取图片描述
        attributes_of_item = pyquery_object.find("#description p img").attr('src')
        if isinstance(attributes_of_item, str):
            attr = attributes_of_item
        else:
            # 图片没有加载出来，就获取
            attributes_of_item = pyquery_object.find('#description div.ke-post').text()
            if isinstance(attributes_of_item, str):
                if len(attributes_of_item) > 0:
                    attr = attributes_of_item
    if attr:
        print("[item_attribute]: {}".format(attr))
    else:
        # print("Failed to get item attribute.")
        raise UserWarning("Failed to get item attribute.")
    return attr


# 获取天猫商品的销量
def get_tmall_item_sell_num(pyquery_object):
    sell_num = None
    sell_num_node = pyquery_object.find('.tm-ind-reviewCount .tm-count').text()
    if isinstance(sell_num_node, str):
        sell_num = sell_num_node.strip()
    if sell_num:
        print("[sell_num]: {}".format(sell_num))
    else:
        print("Failed to get sell num.")
    return sell_num


# 获取天猫商品的评论数量
def get_tmall_item_rate_num(pyquery_object):
    rate_num = None
    rate_num_node = pyquery_object.find('.tm-ind-sellCount .tm-count').text()
    if isinstance(rate_num_node, str):
        rate_num = rate_num_node.strip()
    if rate_num:
        print("[rate_num]: {}".format(rate_num))
    else:
        print("Failed to get rate num.")
    return rate_num


# 获取天猫商品的原价
def get_tmall_item_origin_price(pyquery_object):
    origin_price = None
    origin_price_node = pyquery_object.find('#J_PromoPrice .tm-price').text()
    if isinstance(origin_price_node, str):
        origin_price = origin_price_node.strip()
    if origin_price:
        print("[origin_price]: {}".format(origin_price))
    else:
        print("Failed to get origin price.")
    return origin_price


# 获取天猫商品的当前价格
def get_tmall_item_current_price(pyquery_object):
    current_price = None
    current_price_node = pyquery_object.find('#J_StrPriceModBox .tm-price').text()
    if isinstance(current_price_node, str):
        current_price = current_price_node.strip()
    if current_price:
        print("[current_price]: {}".format(current_price))
    else:
        print("Failed to get current price.")
    return current_price


# 获取天猫商品的名字
def get_tmall_item_name(pyquery_object):
    # 初始化
    name_of_item = None
    # 获取商品名字节点
    name_of_item_node = pyquery_object.find('div.tb-detail-hd').text()
    if isinstance(name_of_item_node, str):
        if len(name_of_item_node) > 0:
            name_of_item = re.sub("\s+", " ", name_of_item_node)
    if name_of_item:
        print("[item_name]: {}".format(name_of_item))
    else:
        raise UserWarning("Failed to get item item_name.")
    return name_of_item


# 获取淘宝的商品ID
def get_taobao_item_id(pyquery_object):
    item_id = None
    # 通过一个图片的链接去匹配itemid
    item_and_shop_id = pyquery_object.find('.tb-main-pic a').attr('href')
    if isinstance(item_and_shop_id, str):
        item_and_shop_id_obj = re.search("itemId=(\d+)", item_and_shop_id)
        item_id = item_and_shop_id_obj.group(1)
    else:
        # 通过head里面的一个链接去匹配itemid
        item_link = pyquery_object("head link[rel='canonical']").attr('href')
        if isinstance(item_and_shop_id, str):
            item_and_shop_id_obj = re.search("(\d+)", item_link)
            item_id = item_and_shop_id_obj.group(1)
    if item_id:
        print("[item_id]: {}".format(item_id))
    else:
        # print("Failed to get item id.")
        raise UserWarning("Failed to get item id.")
    return item_id


# 获取淘宝商店的ID
def get_taobao_shop_id(pyquery_object):
    # 通过一个图片的链接去匹配shopid
    shop_id = None
    item_and_shop_id = pyquery_object.find('.tb-main-pic a').attr('href')
    if isinstance(item_and_shop_id, str):
        item_and_shop_id_obj = re.search("shopId=(\d+)", item_and_shop_id)
        shop_id = item_and_shop_id_obj.group(1)
    else:
        # 通过head里面的一个链接去匹配itemid
        content = pyquery_object.find('meta[name="microscope-data"]').attr('content')
        if isinstance(content, str):
            shop_id = re.search("shopId=(\d+)", content).group(1)
    if shop_id:
        print("[shop_id]: {}".format(shop_id))
    else:
        # print("Failed to get shop id.")
        raise UserWarning("Failed to get shop id.")
    return shop_id


# 获取淘宝商店的名字
def get_taobao_shop_name(pyquery_object):
    # 初始化store_name为None
    store_name = None
    # 直接通过商店名字的节点获取
    store_name_node = pyquery_object.find(".shop-name-title").attr("title")
    if isinstance(store_name_node, str):
        if len(store_name_node) > 0:
            store_name = store_name_node
    if not store_name:
        # 通过一种节点获取
        store_name_node = pyquery_object.find('.tb-shop-name a').text()
        if isinstance(store_name_node, str):
            if len(store_name_node) > 0:
                store_name = store_name_node.strip()
    if not store_name:
        # 通过另一种节点获取
        store_name_node = pyquery_object.find('.shop-name-wrap a.shop-name-link').text()
        if isinstance(store_name_node, str):
            if len(store_name_node) > 0:
                store_name = store_name_node.strip()
    if store_name:
        print("[shop_id]: {}".format(store_name))
    else:
        # print("Failed to get store name.")
        raise UserWarning("Failed to get store name.")
    return store_name


# 获取淘宝商店的链接
def get_taobao_shop_link(pyquery_object):
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


# 获取淘宝商品描述
def get_taobao_item_attr(pyquery_object):
    # 初始化attr为None
    attr = None
    # 获取商品的文字描述
    attributes_of_item = pyquery_object.find('.attributes-list').text()
    # 去掉换行和多余的空格
    if isinstance(attributes_of_item, str):
        if len(attributes_of_item) > 0:
            attr = attributes_of_item.strip()
            attr = re.sub("\s+", " ", attr)
    if not attr:
        # 没有文字描述的，获取图片描述
        attributes_of_item = pyquery_object.find("#J_DivItemDesc img[align='absmiddle']").attr('src')
        if isinstance(attributes_of_item, str):
            attr = attributes_of_item
        else:
            # 有时候图片被设定不显示
            attributes_of_item = pyquery_object.find('#J_DivItemDesc img[style="display: block;width: 100.0%;"]').attr('src')
            if isinstance(attributes_of_item, str):
                attr = attributes_of_item
    if attr:
        print("[item_attribute]: {}".format(attr))
    else:
        # print("Failed to get item attribute.")
        raise UserWarning("Failed to get item attribute.")
    return attr


# 获取淘宝商品销量数据
def get_taobao_item_sell_num(pyquery_object):
    # 初始化sell_count为None
    sell_count = None
    sell_count_noe = pyquery_object.find('#J_SellCounter').text()
    if isinstance(sell_count_noe, str):
        sell_count = sell_count_noe.strip()
    if sell_count:
        print("[item_sell_num]: {}".format(sell_count))
    else:
        print("Failed to get item sell number.")
    return sell_count


# 获取淘宝商品评价数量
def get_taobao_item_rate_num(pyquery_object):
    # 初始化rate_num为None
    rate_num = None
    rate_num_node = pyquery_object.find('#J_RateCounter').text()
    if isinstance(rate_num_node, str):
        rate_num = rate_num_node.strip()
    if rate_num:
        print("[item_rate_num]: {}".format(rate_num))
    else:
        print("Failed to get item rate number.")
    return rate_num


# 获取淘宝商品的原价，有些限制了登录才显示，允许为空值
def get_taobao_item_origin_price(pyquery_object):
    # 初始化origin_price为None
    origin_price = None
    origin_price_node = pyquery_object.find('#J_StrPrice').text()
    if isinstance(origin_price_node, str):
        origin_price = origin_price_node.strip()
    if origin_price:
        print("[origin_price]: {}".format(origin_price))
    else:
        print("Failed to get item origin price.")
    return origin_price


# 获取淘宝商品的现价，有些限制了登录才显示，允许为空值
def get_taobao_item_current_price(pyquery_object):
    # 初始化current_price为None
    current_price = None
    current_price_node = pyquery_object.find('#J_PromoPriceNum').text()
    if isinstance(current_price_node, str):
        current_price = current_price_node.strip()
    if current_price:
        print("[current_price]: {}".format(current_price))
    else:
        print("Failed to get item current price.")
    return current_price


# 获取淘宝商品的名称
def get_taobao_item_name(pyquery_object):
    # 初始化item_name为None
    item_name = None
    item_name_node = pyquery_object.find('#J_Title .tb-main-title').text()
    if isinstance(item_name_node, str):
        if len(item_name_node) > 0:
            item_name = re.sub("\s+", " ", item_name_node)
    if item_name:
        print("[item_name]: {}".format(item_name))
    else:
        raise UserWarning("Failed to get item item_name.")
    return item_name


'''定义需要访问的非商品的链接'''
visit_patten = ["//shop\d+.taobao.com",
                "//[a-z-A-Z.]{6,20}.taobao.com",
                "//[a-z-A-Z.]{6,20}.tmall.com",
                "//shop\d+.taobao.com/category-\d+.htm"]
'''定义需要的商品链接格式'''
item_patten = ["//detail.tmall.com/item.htm[0-9-a-z_A-Z.?&=]+id=\d+",
               "/item.taobao.com/item.htm[0-9-a-z_A-Z.?&=]+id=\d+"]


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
            date = d1 - datetime.timedelta(days=25)
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
            date = d1 - datetime.timedelta(days=25)
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            db.store_info.insert_one({"link": url, "date": date})
            print("The current saved link: %s" % url)
        else:
            print("Link %s is exist in the db." % url)


# 保存详情
def save_detail_info(link, data):
    conn = MongoClient('localhost', 27017)
    db = conn.taobao_spider
    db.item_info.update_one(filter={'link': link}, update={'$set': data}, upsert=True)


# 按照访问时间的顺序排列，获取指定数量的商品链接，并返回列表。
def get_item_link_from_db(num=5):
    conn = MongoClient('localhost', 27017)
    db = conn.taobao_spider
    filter_link = {'visited': {'$ne': "1"}}
    search_res = db.item_info.find(filter_link, limit=num, no_cursor_timeout=True).sort("date", -1)  # '1'是顺序，'-1'是倒叙
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
        get_item_link_from_db(250)
    # 获取一个商品链接
    item_link = waiting_link_list.pop()
    # item_link = "https://item.taobao.com/item.htm?id=584779112890"
    # 通过webdriver获取页面，以及实际跳转后的链接
    page_content, current_link = download_by_webdrive(item_link)
    if page_content:
        # 获取更多商品或者商店链接
        links = get_item_links(page_content)
        # 保存链接到数据库
        for got_link in links:
            save_links(got_link)
        # 获取商品信息
        info = get_detail_info(page_content, current_link)
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
            print("##########################\n", page_content, "\n############################")
            print("[main]: type of info is %s" % type(info), info)
            # time.sleep(15)
    print("#" * 100)
