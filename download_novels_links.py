import BiQuGeDownloader
from pymongo import MongoClient
import re
from urllib.parse import urljoin


def d_links(url, db):
    hunter = BiQuGeDownloader.BiQuGeDownloader()
    str_of_result = hunter.open_url_return_str(url)
    dict_of_chapter = hunter.get_contents(str_of_result, wanted="link", baseurl=url)
    i = 1
    for id_of_chapter, (name_of_chapter, link_of_chapter) in dict_of_chapter.items():
        filter_link = {'id_of_chapter': {'$eq': id_of_chapter}}
        search_res = db.links_for_books.find_one(filter_link)
        if not search_res:
            db.links_for_books.insert(
                {"id_of_chapter": id_of_chapter, "name_of_chapter": name_of_chapter, "link_of_chapter": link_of_chapter,
                 "status_of_visited": 0})
            print("%d links have added into database" % i, "the info as following: ")
            print(id_of_chapter, name_of_chapter, link_of_chapter)
            i += 1
        else:
            print("This link is existed, its id is %s" % id_of_chapter)
    # conn.close()


hunter = BiQuGeDownloader.BiQuGeDownloader()
str_of_result = hunter.open_url_return_str('http://www.biqugex.com/')
conn = MongoClient('localhost', 27017)
db = conn.novels
links = re.findall('/book_\d+/', str_of_result)
j = 1
for link in list(set(links)):
    print("#"*100)
    link = urljoin('http://www.biqugex.com/', link)
    d_links(link, db)
    print(j, link)
    j += 1
conn.close()


