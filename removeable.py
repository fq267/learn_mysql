import urllib
import random
import time
from pyquery import PyQuery as pq

i = 0
while i < 300 :
    url = "http://www.biqugex.com/book_32416/" + str(i+14109933) + ".html"
    print(url)
    res = urllib.request.urlopen(url)
    strResult = (res.read().decode('gbk'))
    pyquery_object = pq(strResult)
    content = pyquery_object("#content").text()
    name = pyquery_object(".content h1").text()
    print("here is ", name)
    filePath = '/Users/fanq/Workspace/learn_mysql/' + 'chaojitoushiyan' + '.txt'
    file_object = open(filePath, mode='a', encoding='utf-8')
    try:
        file_object.write(name)
        file_object.write("\n")
        file_object.write(content)
        file_object.write("\n")
    finally:
        file_object.close()
    t = random.randint(2,8)
    print("here will sleep for ", t, " seconds")
    time.sleep(t)
    i += 1