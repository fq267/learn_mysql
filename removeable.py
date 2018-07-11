import requests
import random
import time
from pyquery import PyQuery as pq
from urllib.parse import urljoin


def download_pic(url, re_times=3):
    base_url = "https://car%d.autoimg.cn" % random.randint(1, 3)
    url = url.replace('t_autohomecar', '1024x0_1_q87_autohomecar')
    url = url[url.find("/cardfs"):]
    print("1", url)
    url = urljoin(base_url, url)
    print("2", url)
    try:
        res = requests.get(url, timeout=3)
        if res.status_code >= 300 and re_times > 0:
            print("retry times %s" % re_times)
            time.sleep(2)
            return download_pic(url, re_times - 1)
        elif res.status_code < 300:
            result_of_download = res.content
            print("http code is ", res.status_code)
            return result_of_download
        else:
            return None
    except Exception as e:
        print("open_url_return_str", e)
        if re_times > 0:
            print("retry times %s" % re_times)
            time.sleep(10)
            return download_pic(url, re_times - 1)
        else:
            raise UserWarning("Something bad happened")


entryurl = "https://car.autohome.com.cn/pic/series/364-10-p2.html"
r = requests.get(entryurl, timeout=3)
pyquery_object = pq(r.text)
i = 1
for item in pyquery_object(".uibox img"):
    link_of_chapter = pq(item).attr("src")
    name_of_chapter = pq(item).attr('title')
    print(i, "name_of_chapter is %s " % name_of_chapter)
    pic_name = "D:\downloaded_pic\%s%s.jpg" % (name_of_chapter, i)
    content = download_pic(link_of_chapter)
    with open(pic_name, 'wb') as file:
        print(i, "pic_name is ", pic_name)
        file.write(content)
        time.sleep(1)
    i += 1
