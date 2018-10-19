import random
import re
import time
from selenium import webdriver
from pymongo import MongoClient
from pyquery import PyQuery as pq


def download_by_webdriver(url, charset='utf-8'):
    '''return page content as string '''
    try:
        # browser = webdriver.PhantomJS()
        # options = webdriver.IeOptions()
        # options.add_argument("--headless")
        browser = webdriver.Ie()
        browser.get(url)
        str_of_result = browser.page_source
        str_of_result = str_of_result.encode('utf-8', 'ignore').decode('utf-8')
    finally:
        browser.close()
        return str_of_result


def read_5_each():
    list_of_threadid_and_link = []
    conn = MongoClient('localhost', 27017)
    db = conn.girls
    search_res = db.girllinks.find(filter={'status_of_visit': 0},
                                   no_cursor_timeout=True).sort("date", 1)  # '1'是顺序，'-1'是倒叙
    conn.close()
    for res in search_res:
        t_id = res['thread_id']
        t_link = res['link']
        pic_links = res['pic_links']
        list_of_threadid_and_link.append((t_id, t_link, pic_links))
    return list_of_threadid_and_link


# def get_links_re(str_res, pattern):
#     print(str_res)
#     links = re.findall(pattern, str_res)
#     links = list(set(links))
#     print("found %s links." % len(links))
#     for link in links:
#         print('get_links_re found link %s ' % link)
#     return links


def get_link_pyquery(str_res, pattern=None):
    pyquery_object = pq(str_res)
    links = []
    for item in pyquery_object("#read_tpc img"):
        link_of_chapter = pq(item).attr('src')
        links.append(link_of_chapter)
    return links


# pic_pattern = 'http://.+/picturespace/upload/image/\d+/\d+.jpg'
id_link_list = []
counter = 1
while True:
    conn = MongoClient('localhost', 27017)
    db = conn.girls
    if len(id_link_list) < 2:
        id_link_list = read_5_each()[100:]
    (thread_id, thread_link, p_links) = id_link_list.pop(0)
    if len(p_links) > 0:
        print("%s There are %s pic links for %s thread." % (counter, p_links, thread_id))
    elif 'pw' in thread_link:
        print("Will download the %s thread at %s ." % (thread_id, time.ctime()))
        time.sleep(random.randint(1, 10))
        thread_page = download_by_webdriver(thread_link)
        pic_links = get_link_pyquery(thread_page)
        print('pic_link ', pic_links)
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        db.girllinks.update_one(filter={'link': thread_link},
                                update={'$set': {"pic_links": pic_links,
                                                 "status_of_visit": 0,
                                                 "date": date}}, upsert=True)
    else:
        db.girllinks.delete_one(filter={'link': thread_link})
        print("link is bad, pass %s. " % thread_link)
    counter += 1
    conn.close()
    time.sleep(random.randint(1, 20))
