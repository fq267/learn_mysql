import time

from pymongo import MongoClient


conn = MongoClient('localhost', 27017)
db = conn.novels
filter_link = {'book_name': {'$eq': '武动乾坤'}}
search_res = db.contents.find(filter=filter_link, projection={"id_of_chapter": 1,
                              "content": 1, "chapter_name": 1}).sort("id_of_chapter", 1)
i = 1
for res in search_res:
    print(i, res.get("chapter_name"), res.get("id_of_chapter"))
    with open("wudongqiankun.txt", mode="a") as f:
        if i >= 0:
            # f.write(res.get("chapter_name"))
            # f.write("\n")
            f.write(res.get("content").encode('gbk', 'ignore').decode('gbk', 'ignore'))
            f.write("\n")
            # time.sleep(0.5)
    i += 1
conn.close()
