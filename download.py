from pyquery import PyQuery as pq
import urllib

url = 'http://www.useragentstring.com/pages/useragentstring.php?name=All'
res = urllib.request.urlopen(url)
strResult = (res.read().decode('iso-8859-1'))
print(type(strResult))
print(strResult)
d = pq(strResult)

try:
    fh = open("/home/fanq/Workspace/learn_mysql/user_agent.log", "w")
    for item in d("#liste ul li a"):
        # print(pq(item).text())
        fh.write(pq(item).text())
        fh.write('\n')
except IOError:
    print("Error: 没有找到文件或读取文件失败")
else:
    print("内容写入文件成功")
    fh.close()
