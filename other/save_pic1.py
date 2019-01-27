import logging
import os
import random
import time

from pymongo import MongoClient
import requests


def read_5_each(num=5):
    conn = MongoClient('localhost', 27017)
    db = conn.girls
    list_of_threadi_and_links = []
    search_res = db.girllinks.find(filter={'status_of_visit': 0},
                                   limit=num, no_cursor_timeout=True).sort("date", -1)  # '1'是顺序，'-1'是倒叙
    conn.close()
    for res in search_res:
        t_id = res['thread_id']
        p_links = res['pic_links']
        list_of_threadi_and_links.append((t_id, p_links))
    return list_of_threadi_and_links


def download_pic(url, re_times=3):
    try:
        res = requests.get(url, timeout=5)
        if res.status_code >= 300:
            raise UserWarning("http code is larger than 300.")
        else:
            # print("succeed downloaded")
            return res
    except Exception as e:
        print("open_url_return_str", e)
        if re_times > 0:
            print("retry times %s" % re_times)
            # time.sleep(1)
            return download_pic(url, re_times - 1)
        else:
            # raise UserWarning("Something bad happened")
            print("failed to download this link %s" % url)


def update_one_thread(thread_id, date):
    conn = MongoClient('localhost', 27017)
    db = conn.girls
    db.girllinks.update_one(filter={'thread_id': thread_id},
                            update={'$set': {"status_of_visit": 1, "date": date}}, upsert=True)
    conn.close()


if __name__ == "__main__":
    id_links_list = []
    counter_for_all_pics = 1
    counter_for_thread = 1
    while True:
        if len(id_links_list) < 2:
            id_links_list = read_5_each(num=100)[51:]
        counter_for_each_thread_pics = 1
        (thread_id, pic_links) = id_links_list.pop(0)
        for link in pic_links:
            content = download_pic(link, re_times=6)
            if content:
                id_for_pic = str(thread_id) + str(counter_for_each_thread_pics)
                pic_name = 'C:\Workspace\downloaded_pic\girls\\' + id_for_pic + '.jpg'
                try:
                    with open(pic_name, 'wb') as file:
                        print(counter_for_thread, counter_for_all_pics, counter_for_each_thread_pics, "pic_name is ",
                              pic_name)
                        file.write(content.content)
                        time.sleep(random.random())
                except Exception:
                    pass
                counter_for_each_thread_pics += 1
                counter_for_all_pics += 1
                # db.girlpics.insert_one({"content": content})
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        try:
            update_one_thread(thread_id, date)
            counter_for_thread += 1
            logging.info("all links for %s downloaded." % thread_id)
        except Exception as e:
            print(e)
        finally:
            print("download for ", thread_id)


