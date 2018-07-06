import BiQuGeDownloader
from pymongo import MongoClient
import time

conn = MongoClient('localhost', 27017)
db = conn.novels
queryArgs = {'status_of_visited ': {'$ne': 1}}
search_res = db.links_for_books.find(queryArgs).sort("id_of_chapter", -1)
print(type(search_res))
for record in search_res:
    print("id_of_chapter  = %s" % record['id_of_chapter'])
    updateFilter = {'id_of_chapter': record['id_of_chapter']}
    updateRes = db.links_for_books.update_one(filter=updateFilter, update={'$set': {"status_of_visited": 1}},
                                              upsert=True)
    time.sleep(0.8)
conn.close()
