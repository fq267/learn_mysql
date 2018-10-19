import re
import time
import requests
from urllib.parse import urljoin
from pyquery import PyQuery as pq


class BiQuGeDownloader(object):
    def __init__(self):
        pass

    def open_url_return_str(self, url, re_times=3):
        try:
            res = requests.get(url, timeout=5)
            result_of_download = res.text
            print("succeed downloaded")
            return result_of_download
        except Exception as e:
            print("open_url_return_str", e)
            if re_times > 0:
                print("retry times %s" % re_times)
                time.sleep(4)
                return self.open_url_return_str(url, re_times - 1)
            else:
                raise UserWarning("Something bad happened")

    '''获取所有链接，去重。返回字典，key是每章的序号，value是元组，包含章名和链接'''

    def get_contents(self, str_of_result, wanted='link', baseurl=None):
        pyquery_object = pq(str_of_result)
        if wanted == 'link':
            dict_of_content = {}
            for item in pyquery_object(".listmain a"):
                name_of_chapter = pq(item).text()
                link_of_chapter = pq(item).attr('href')
                link_of_chapter = urljoin(baseurl, link_of_chapter)
                id_of_chapter = re.findall(r'(\d+)\.html', link_of_chapter)[0]
                id_of_chapter = int(id_of_chapter)
                print(id_of_chapter)
                print(name_of_chapter)
                print(link_of_chapter)
                if id_of_chapter in dict_of_content:
                    continue
                else:
                    dict_of_content[id_of_chapter] = (name_of_chapter, link_of_chapter)
            return dict_of_content
        else:
            dict_of_content = {'content': pyquery_object("#content").text(),
                               'book_name': pyquery_object(".path").find('a').eq(1).text(),
                               'chapter_name': pyquery_object(".content").find('h1').text()}
            return dict_of_content

