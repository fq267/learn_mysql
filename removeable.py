import urllib, re, time
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from pymongo import MongoClient

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
        link_of_chapter = urljoin(entryUrl, link_of_chapter)
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

conn = MongoClient('localhost', 27017)
db = conn.novels
dict_of_chapter = get_all_links(open_url_return_str(entryUrl))
for id_of_chapter, (name_of_chapter, link_of_chapter) in dict_of_chapter.items():
    print(id_of_chapter, name_of_chapter, link_of_chapter)
    db.links_for_books.insert(
        {"id_of_chapter": id_of_chapter, "name_of_chapter": name_of_chapter, "link_of_chapter": link_of_chapter,
         "status_of_visited": 0})

conn.close()
