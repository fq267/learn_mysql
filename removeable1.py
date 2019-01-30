# import BiQuGeDownloader
# from pymongo import MongoClient
# import time
#
#
# def get_links_from_db():
#     conn = MongoClient('localhost', 27017)
#     db = conn.novels
#     filter_link = {'status_of_visited': {'$eq': 0}}
#     search_res = db.links_for_books.find(filter_link).sort("id_of_chapter", -1)
#     conn.close()
#     return search_res
#
#
# conn = MongoClient('localhost', 27017)
# db = conn.novels
# search_res = get_links_from_db()
# for record in search_res:
#     link_for_chapter = record['link_of_chapter']
#     id_of_chapter = record['id_of_chapter']
#     print("id_of_chapter  = %s, link_of_chapter = %s" % (id_of_chapter, link_for_chapter))
#     hunter = BiQuGeDownloader.BiQuGeDownloader()
#     try:
#         res = hunter.open_url_return_str(link_for_chapter, re_times=9)
#         res_content = hunter.get_contents(res, wanted='content')
#         res_content['id_of_chapter'] = id_of_chapter
#         print("book_name is %s, chapter_name is %s, content is %s" %
#               (res_content.get('book_name'), res_content.get('chapter_name'), res_content.get('content')[100:120]))
#         updateFilter = {'id_of_chapter': record['id_of_chapter']}
#         updateRes = db.links_for_books.update_one(filter=updateFilter, update={'$set': {"status_of_visited": 1}},
#                                                   upsert=True)
#         db.contents.insert_one(res_content)
#     except UserWarning as e:
#         print(e)
#     finally:
#         conn.close()
#         time.sleep(0.8)
#         print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
#         print("#" * 100, "\n" * 2)
# from urllib.parse import urlsplit
# from selenium import webdriver
#
#
# url = "https://click.simba.taobao.com/cc_im?spm=a231k.8165028.0782702702.2&prepvid=300_11.20.213.194_207447_1548384377662&extra=&p=%B7%B6%CE%AC%CE%F5&s=352232824&k=537&e=ddnYyTYt5M4UEqxn%2BXKpXztgY80V6ovyNHakd%2F%2BNJnpyrIrSe9pSX8u4w7zFzGo8y2g3ofs7fbNvXLRVVofNNkrYGD8eSdSlY60bNw9uqFqfH8mL7LklPQ1anOn5phhuVA3JXmyaVSFldRuabr7NM%2B4YykQcGk%2Bvs8mFXWA%2Fo7exsLibXFtOR6oXtYrXn%2FuigMpO8Fn2D9UZDKzceq%2B6A0TG5ug4UI1nJZ4euou77qZL6CtiNcBeCcS9PWd03gsRGTmv3OcrsMwedUj6%2BK%2B6tPbfnObB6gDBvejGa6OWVXXwmyaAR%2FluVXf%2BEkE4QLjnItE9AC497p6yAzGYNLIc55oEBO7pqTDoDKOcfzdxSGRno%2BOQt26dh4dhzRcWb7niBgAwS5IxtAmBgMCrByVXTmuVFJ9TLANN%2F4L21lLul8fIWIn0hXH6rZR1oTJ%2BQLFxLnu0jgtsgBwpCOdaS6BqgB5Fml6cbB5Eq25jp%2B1jydtKHIDkeWxSYuJHPdfBL1sQBoyYfzf51e3K1tJzfD%2FB4A%3D%3D"
# driver = webdriver.Chrome()
# driver.get(url)
# print(driver.current_url)
# driver.close()


#
# from pymongo import MongoClient
# conn = MongoClient('localhost', 27017)
# db = conn.taobao_spider
# db.item_info.update({},{'$rename' : {"link" : "link_of_item1"}}, False, True)

import requests

proxies = {
    "http": "http://119.101.124.165:9999"  # 代理ip
}

headers = {
    "User_Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
}

# http_url = "http://you.163.com/item/list?categoryId=1013001&subCategoryId=1037001"
http_url = "http://you.163.com/item/list?categoryId=1005000"
res = requests.get(url=http_url, timeout=30)
if res.status_code == 200:
    print("done")
    print(res.text)
else:
    print("failed")
