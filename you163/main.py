#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from you163.get_item_info import entry as info_entry
from you163.get_item_links import entry as link_entry
from you163.get_proxy_ip import entry as ip_entry
import datetime


while True:
    today = datetime.date.today()
    formatted_today = today.strftime('%d')
    if (int(formatted_today) % 2) == 0:
        print("#" * 50, "执行爬取商品链接的脚本", "#" * 50)
        # link_entry()
    print("#" * 50, "执行爬取代理IP的脚本", "#" * 50)
    ip_entry()
    print("#" * 50, "执行爬取商品详情的脚本", "#" * 50)
    info_entry()