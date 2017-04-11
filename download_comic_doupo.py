import time
from pyquery import PyQuery as pq
import urllib

entryUrl = 'http://www.chuiyao.com/manhua/3670/'


def open_url_return_str(url):
    res = urllib.request.urlopen(url)
    strResult = (res.read().decode('utf-8'))
    return strResult


def all_chapters_in_dict_with_name_and_link(pagestr):
    pyqueryObject = pq(pagestr)
    dictOfChapter = {}
    for item in pyqueryObject(".cy_plist ul li a"):
        nameOfChapter = pq(item).text()
        linkOfChapter = pq(item).attr('href')
        dictOfChapter[nameOfChapter] = linkOfChapter
    return dictOfChapter


homePage = open_url_return_str(entryUrl)

dictOfChapter = all_chapters_in_dict_with_name_and_link(homePage)
for kForChapter, vForChapter in dictOfChapter.items():
    print(vForChapter)
    chapterPage = open_url_return_str(vForChapter)
    print(chapterPage)
    # filePath = '/home/fanq/Workspace/learn_mysql/' + kForChapter + \
    #            kForPage + '.jpg'
    # pic = urllib.request.urlopen(vForPage)
    # f = open(filePath, 'wb')
    # f.write(pic.read())
    # f.close()
    # time.sleep(2)
