import re

d1 = "series/66-1.html"
p = re.compile('-p(\d+)')
page_num =p.findall(d1)
print(page_num)