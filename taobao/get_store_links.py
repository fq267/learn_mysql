#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re
import datetime
import random

from selenium import webdriver
from urllib.parse import urljoin
from pymongo import MongoClient

'''定义抓取入口，两种需要匹配的链接'''
# home_page = "https://www.taobao.com/markets/tbhome/cool-shop"
home_page = "https://jupage.taobao.com/wow/tttj/act/index"
'''定义需要访问的非商品的链接'''
visit_patten = ["//shop\d+.taobao.com", "//\w+.taobao.com", "//\w+.tmall.com", "//jupage.taobao.com/\w+/\w+/\w+/index"]
'''定义需要的商品链接格式'''
item_patten = ["//detail.tmall.com/item.htm[0-9-a-z_A-Z.?&=]+id=\d+",
               "/item.taobao.com/item.htm[0-9-a-z_A-Z.?&=]+id=\d+"]


def parse_page_by_patten(patten, content):
    compile_obj = re.compile(patten)
    return compile_obj.findall(content)


def download_by_webdriver(url, visit_type="visit", charset='gbk'):
    '''return page content as string '''
    print("begin download the link %s" % url)
    # driver = webdriver.Chrome()
    driver = webdriver.PhantomJS()
    driver.get(url)
    if visit_type == "home":
        content = driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
        driver.quit()
    elif visit_type == "visit":
        if url.find("cool-shop") > 0:  # 判断当前网页是否需要翻滚
            try:
                for i in range(0, 20):
                    print("scroll time %d." % i)
                    driver.execute_script("window.scrollTo(0, 100);")
                    time.sleep(0.5)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    content = driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
                    driver.quit()
            except Exception as e:
                content = ""
                print(e)
                driver.quit()
        elif url.find("jupage") > 0:  # 判断当前网页是否需要点击下一页
            content = ""
            try:
                for i in range(0, 100):
                    print("click %d times" % i)
                    driver.execute_script('document.querySelector(".pager a.next ").click()')
                    time.sleep(random.randint(2, 10))
                    content += driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
                    print(len(content))
                    driver.quit()
            except Exception as e:
                content = ""
                print(e)
                driver.quit()
        else:
            try:
                for i in range(0, 3):
                    print("scroll time %d." % i)
                    driver.execute_script("window.scrollTo(0, 100);")
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.randint(2, 4))
                    content = driver.page_source.encode(charset, "ignore").decode(charset, 'ignore')
                    driver.quit()
            except Exception as e:
                content = ""
                print(e)
    return content


def parse_page(page_content):
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


def save_to_store(url, db):
    filter_link = {'link': {'$eq': url}}
    search_res = db.store_info.find_one(filter_link)
    if not search_res:
        d1 = datetime.datetime.now()
        date = d1 - datetime.timedelta(days=10)
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        db.store_info.insert_one({"link": url, "date": date})
        print("The current saved link: %s" % url)
    else:
        print("This link is existed in db: %s" % url)


def save_to_item(url, db):
    filter_link = {'link': {'$eq': url}}
    search_res = db.item_info.find_one(filter_link)
    if not search_res:
        d1 = datetime.datetime.now()
        date = d1 - datetime.timedelta(days=10)
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        db.item_info.insert_one({"link": url, "date": date})
        print("The current saved link: %s" % url)
    else:
        print("This link is existed in db: %s" % url)


def main():
    black_links = file_operate("/Users/fanq/Workspace/learn_mysql/taobao/black_links", mode="r")
    waiting_links_from_file = file_operate("/Users/fanq/Workspace/learn_mysql/taobao/waiting_links", mode="r")
    visited_links_from_file = file_operate("/Users/fanq/Workspace/learn_mysql/taobao/visited_links", mode="r")
    conn = MongoClient('localhost', 27017)
    db = conn.taobao_spider
    waiting_links = set()
    waiting_links.add(home_page)
    waiting_links = waiting_links | set(waiting_links_from_file)
    visited_links = set(visited_links_from_file)
    while len(waiting_links) > 0:
        print("#" * 100)
        print("There are %d links waiting for visit" % len(waiting_links))
        print("There are %d links have been visited" % len(visited_links))
        link = waiting_links.pop()
        if not link in visited_links:
            page = download_by_webdriver(link, visit_type="visit")
            visited_links.add(link)
            file_operate("/Users/fanq/Workspace/learn_mysql/taobao/waiting_links", "w", list(waiting_links))
            for url in parse_page(page):
                if url.startswith('http'):
                    pass
                else:
                    url = urljoin("https:", url)
                if url.find("item.htm") > 0:
                    save_to_item(url, db)
                elif url.find("shop") > 0:
                    waiting_links.add(url)
                    save_to_store(url, db)
                elif not url in black_links:
                    waiting_links.add(url)
    conn.close()


def file_operate(path, mode="r", content=None):
    if mode == "r" or mode == "read":
        with open(path, mode) as f:
            black_links = f.readlines()
        f.close()
        return black_links
    elif mode == "w" or mode == "write":
        with open(path, mode) as f:
            for link in content:
                f.write(link + "\n")
        f.close()
        return None
    elif mode == "a" or mode == "append":
        with open(path, mode) as f:
            f.write(content)
        f.close()
        return None


if __name__ == '__main__':
    main()
