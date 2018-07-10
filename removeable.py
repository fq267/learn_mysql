import requests

entryurl="https://car.autohome.com.cn/pic/series-s25892/135-1.html#pvareaid=2042222"
r = requests.get(entryurl)
print(r.status_code, r.encoding)
print(type(r.text))