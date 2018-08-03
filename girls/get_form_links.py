import datetime
import random
from urllib.parse import urljoin
import requests
import re
import time
from selenium import webdriver
from pymongo import MongoClient


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
        time.sleep(15)
    finally:
        browser.close()
        return str_of_result


def get_links_re(str_res, pattern):
    links = re.findall(pattern, str_res)
    links = list(set(links))
    for link in links:
        print('get_links_re found link %s ' % link)
    return links


def generate_form_links(form_list, start_page=1, end_page=5):
    f_links = []
    for form_id in form_list:
        if end_page >= start_page:
            for i in range(start_page, end_page):
                f_links.append('http://n2.lufi99.info/pw/thread.php?fid=%s&page=%s' % (form_id, i))
        else:
            print("end_page should larger than or equal to start_page")
    return f_links


def download_pic(url, re_times=3):
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
            raise UserWarning("Something bad happened")
            # return None


def get_thread_links(f_link):
    t_links = []
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    form_page = download_by_webdriver(f_link)
    print("download link: %s, length of the result is %s" % (f_link, len(form_page)))
    for t_link in get_links_re(form_page, thread_pattern):
        t_link = urljoin('http://n2.lufi99.info/pw/', t_link)
        t_links.append(t_link)
        t_links = list(set(t_links))
    return t_links


if __name__ == '__main__':
    form_list = [114, 21, 49, 14, 16]
    thread_pattern = 'htm_data/\d+/\d+/1[1-9]\d+.html'
    all_pic_links = []
    times = 1
    conn = MongoClient('localhost', 27017)
    db = conn.girls
    form_links = generate_form_links(form_list, end_page=3)
    for form_link in form_links:
        thread_links = get_thread_links(form_link)
        print("第%s页论坛页面后，获取到的页面链接数量为%s" % (times, len(thread_links)))
        times += 1
        time.sleep(random.randint(1, 10))
        for thread_link in thread_links:
            comp = re.compile('(\d+).html')
            thread_id = comp.findall(thread_link)[0]
            # thread_page = download_by_webdriver(thread_link)
            filter_link = {'thread_id': {'$eq': thread_id}}
            search_res = db.serieslinks.find_one(filter_link)
            if not search_res:
                d1 = datetime.datetime.now()
                date = d1 - datetime.timedelta(days=10)
                date = date.strftime('%Y-%m-%d %H:%M:%S')
                # pic_links = get_links_re(thread_page, pic_pattern)
                # print('pic_link ', pic_links)
                db.girllinks.update_one(filter={'link': thread_link},
                                        update={'$set': {"link": thread_link, "date": date, "pic_links": [],
                                                "thread_id": thread_id, "status_of_visit": 0}}, upsert=True)
    conn.close()

#
# for pic_link in all_pic_links:
#     content = download_pic(pic_link, re_times=7)
#     if not content:
#         print('this link is bad ', pic_link)
#         continue
#     pic_name = 'C:\Workspace\downloaded_pic\girl\\' + '91_' + str(pic_num) + '.jpg'
#     with open(pic_name, 'wb') as file:
#         print(pic_num, "pic_name is ", pic_name)
#         file.write(content.content)
#     time.sleep(random.random())
#     print("进度是%s : %s " % (pic_num, len(all_pic_links)))
#     pic_num += 1
