# -*- coding: utf-8 -*-
import os
import random
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


def download_by_webdriver(url, scroll_time=5, charset='gbk'):
    '''return page content as string '''
    browser = webdriver.Chrome()
    browser.get(url)
    pos = 0
    for k in range(scroll_time):
        pos += k * 500  # 每次下滚500
        js = "document.documentElement.scrollTop=%d" % pos
        browser.execute_script(js)
        time.sleep(1)

    content = browser.page_source.encode(charset, "ignore").decode(charset, 'ignore')
    time.sleep(2)
    browser.close()
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


def download_pic(url, re_times=3):
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
            # time.sleep(1)
            return download_pic(url, re_times - 1)
        else:
            return None


def parse_page_by_patten(patten, content):
    return re.findall(patten, content)


def parse_page_by_bs4(content, patten=None):
    soup = BeautifulSoup(content, features="lxml")
    if patten:
        first_email_id = soup.find(src=patten)
    return first_email_id


def write_name_into_file(content_name):
    searched_path = "C:\Workspace\learn_mysql\get_people_pics\searched_names"
    with open(searched_path, 'a', encoding="utf-8", errors='ignore') as f:
        f.write(content_name)
        f.write("\n")


def get_name_from_file(path):
    with open(path, 'r', encoding="utf-8", errors='ignore') as f:
        names = set(f.readlines())
    return names


def get_url_by_file(path):
    all_names = get_name_from_file(path)
    print("Found %s names" % len(all_names))
    searched_names = get_name_from_file("C:\Workspace\learn_mysql\get_people_pics\searched_names")
    urls = []
    for name in all_names - searched_names:
        name = name
        base_url = "https://cn.bing.com/images/search?q="
        url = base_url + name
        urls.append(url.strip())
    return urls


path = 'C:\Workspace\learn_mysql\get_people_pics\\names.txt'
all_urls = get_url_by_file(path)
p = re.compile(r"(https://tse\d-mm.cn.bing.net/th\?id=[\w\.]{20,45}?)&")
i = 0
for url in all_urls:
    print(i, "url is ", url)
    content = download_by_webdriver(url, scroll_time=2)
    all_links = parse_page_by_patten(p, content)
    print(len(all_links))
    all_links = set(all_links)
    print(len(all_links))
    person_name = url.split("=")[-1]
    dir_path = os.path.join(os.getcwd(), person_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    j = 1
    for link in all_links:
        res = download_pic(url=link, re_times=5)
        pic_name = "%s\%s.jpg" % (dir_path, j)
        with open(pic_name, 'wb') as file:
            print(i, "pic_name is ", pic_name)
            file.write(res.content)
            time.sleep(random.randint(1, 5))
        j += 1
    write_name_into_file(person_name)
    i += 1

