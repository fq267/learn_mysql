from pyquery import PyQuery as pq
from lxml import etree
import urllib
url='http://www.useragentstring.com/pages/useragentstring.php?name=All'
res = urllib.request.urlopen(url)
strResult=(res.read().decode('iso-8859-1'))
print(type(strResult))
print(strResult)
d = pq(strResult)

# d = pq(url='http://www.useragentstring.com/pages/useragentstring.php?name=All')

print(type(d))
for item in d("#liste ul li a"):
    print(pq(item).text(), '\n')
