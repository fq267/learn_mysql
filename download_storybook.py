import random
import time
from pyquery import PyQuery as pq
import urllib
import re
import urllib.parse as urlparse
import logging

entryUrl = 'http://www.biqugex.com/book_37/'

'''所有访问都使用这个方法'''


def open_url_return_str(url, re_times=3):
    try:
        res = urllib.request.urlopen(url)
        result_of_download = (res.read().decode('gbk'))
        return result_of_download
    except Exception as e:
        print("open_url_return_str", e)
        if re_times > 0:
            print("retry times %s" % re_times)
            time.sleep(10)
            return open_url_return_str(url, re_times - 1)
        else:
            raise UserWarning("Something bad happened")


'''获取所有链接，去重。返回字典，key是每章的序号，value是元组，包含章名和链接'''


def get_all_links(str_of_result):
    pyquery_object = pq(str_of_result)
    dict_of_chapter = {}
    for item in pyquery_object(".listmain a"):
        name_of_chapter = pq(item).text()
        link_of_chapter = pq(item).attr('href')
        id_of_chapter = re.findall(r'(\d+)\.html', link_of_chapter)[0]
        id_of_chapter = int(id_of_chapter)
        print(id_of_chapter)
        print(name_of_chapter)
        print(link_of_chapter)
        if id_of_chapter in dict_of_chapter:
            continue
        else:
            dict_of_chapter[id_of_chapter] = (name_of_chapter, link_of_chapter)
    return dict_of_chapter


'''处理链接，返回所有需要访问的章节。'''


def return_wanted_links(dict_of_links):
    wanted_links = []
    set_of_ids = set(dict_of_links)
    print(set_of_ids)
    list_of_ids = list(dict_of_links)
    list_of_ids.sort()
    for id in list_of_ids:
        try:
            id = int(id)
        finally:
            pass
        if id <= 36681:
            print("here passed ", id)
            continue
        else:
            print("wanted id ", id)
            wanted_links.append((id, dict_of_links.get(id)))
    return wanted_links

'''获取小说文本内容'''


def get_content(link):
    if link.find("http") >= 0:
        # print("0, get_content function found the link is ", link)
        pass
    else:
        link = urlparse.urljoin("http://www.biqugex.com/", link)
        # print("1, get_content function found the link is ", link)
    result = open_url_return_str(link)
    pyquery_object = pq(result)
    content = pyquery_object("#content").text()
    return content

'''文件操作'''


def operation_file(something):
    filePath = 'D:\\Workspace\\learn_mysql\\' + 'wudongqiankun' + '.txt'
    file_object = open(filePath, mode='a', encoding='utf-8')
    try:
        file_object.write(something)
    finally:
        file_object.close()


'''主函数，实现所有逻辑'''
#访问主入口
str_result = open_url_return_str(entryUrl)
all_links = get_all_links(str_result)
wanted = return_wanted_links(all_links)
i = 1
for item in wanted:
    link = item[1][1]
    conten = get_content(link)
    name = item[1][0]
    print("id is ", item[0], "; capter name is ", name, "; link is ", link)
    operation_file(name)
    operation_file("\n")
    operation_file(conten)
    operation_file("\n")
    t = random.randint(2,6)
    print("processing ", str(i), "/ ", str(len(wanted)))
    print("will wait ", t, " seconds")
    time.sleep(t)
    i += 1


#
# def all_chapters_in_dict_with_name_and_link(pagestr):
#     pyqueryObject = pq(pagestr)
#     dictOfChapter = {}
#     for item in pyqueryObject(".cy_plist ul li a"):
#         nameOfChapter = pq(item).text()
#         linkOfChapter = pq(item).attr('href')
#         dictOfChapter[nameOfChapter] = linkOfChapter
#     return dictOfChapter
#
#
# homePage = open_url_return_str(entryUrl)
#
# dictOfChapter = all_chapters_in_dict_with_name_and_link(homePage)
# for kForChapter, vForChapter in dictOfChapter.items():
#     print(vForChapter)
#     chapterPage = open_url_return_str(vForChapter)
#     print(chapterPage)
#
# filePath = '/home/fanq/Workspace/learn_mysql/' + kForChapter + \
#            kForPage + '.jpg'
# pic = urllib.request.urlopen(vForPage)
# f = open(filePath, 'wb')
# f.write(pic.read())
# f.close()
# time.sleep(2)

# import platform
# from bs4 import BeautifulSoup
# from selenium import webdriver
#
# # PhantomJS files have different extensions
# # under different operating systems
# if platform.system() == 'Windows':
#     PHANTOMJS_PATH = './phantomjs.exe'
# else:
#     PHANTOMJS_PATH = './phantomjs'
#
#
# # here we'll use pseudo browser PhantomJS,
# # but browser can be replaced with browser = webdriver.FireFox(),
# # which is good for debugging.
# browser = webdriver.Chrome()
# browser.get('http://w3.afulyu.rocks/pw/')
#
# # let's parse our html
# print(browser.page_source)
# soup = BeautifulSoup(browser.page_source, "html.parser")
# # get all the games
# games = soup.find_all('img')
#
# # and print out the html for first game
# print(games[0].src())
