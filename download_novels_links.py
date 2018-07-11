import BiQuGeDownloader
from pymongo import MongoClient


def d_links(url):
    hunter = BiQuGeDownloader.BiQuGeDownloader()
    str_of_result = hunter.open_url_return_str(url)
    conn = MongoClient('localhost', 27017)
    db = conn.novels
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
    conn.close()


for url in ['http://www.biqugex.com/book_39120/', 'http://www.biqugex.com/book_53174/']:
    d_links(url)

