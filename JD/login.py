import time
from selenium import webdriver

'''定义抓取入口，两种需要匹配的链接'''
homepage = "https://passport.jd.com/new/login.aspx"


def download_by_webdriver(url, charset='gbk'):
    '''return page content as string '''
    browser = webdriver.Ie()
    browser.get(url)
    login_elem = browser.find_element_by_css_selector('.login-tab.login-tab-r')
    print(login_elem.text)
    try:
        login_elem.click()
    finally:
        time.sleep(8)
        browser.close()

download_by_webdriver(homepage)