import BiQuGeDownloader
from pymongo import MongoClient
import time


def get_links_from_db():
    conn = MongoClient('localhost', 27017)
    db = conn.novels
    filter_link = {'status_of_visited': {'$eq': 0}}
    search_res = db.links_for_books.find(filter_link).sort("id_of_chapter", -1)
    conn.close()
    return search_res


conn = MongoClient('localhost', 27017)
db = conn.novels
search_res = get_links_from_db()
for record in search_res:
    link_for_chapter = record['link_of_chapter']
    id_of_chapter = record['id_of_chapter']
    print("id_of_chapter  = %s, link_of_chapter = %s" % (id_of_chapter, link_for_chapter))
    hunter = BiQuGeDownloader.BiQuGeDownloader()
    try:
        res = hunter.open_url_return_str(link_for_chapter, re_times=9)
        res_content = hunter.get_contents(res, wanted='content')
        res_content['id_of_chapter'] = id_of_chapter
        print("book_name is %s, chapter_name is %s, content is %s" %
              (res_content.get('book_name'), res_content.get('chapter_name'), res_content.get('content')[100:120]))
        updateFilter = {'id_of_chapter': record['id_of_chapter']}
        updateRes = db.links_for_books.update_one(filter=updateFilter, update={'$set': {"status_of_visited": 1}},
                                                  upsert=True)
        db.contents.insert_one(res_content)
    except UserWarning as e:
        print(e)
    finally:
        conn.close()
        time.sleep(0.8)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print("#" * 100, "\n" * 2)
