#-*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import requests
import os


class BaiduDoc(object):
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.base_dir = './data/'

    def get_all_doc(self):
        page = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@id='html-reader-go-more']")))
        self.browser.execute_script('arguments[0].scrollIntoView();', page)
        more_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[@class='moreBtn goBtn']")))
        more_btn.click()
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='ie-fix']")))

    def save_to_txt(self, file_name, data):
        with open(os.path.join(self.base_dir, file_name), 'w', encoding='utf-8') as f:
            f.writelines(data)

    def save_all_picture(self, picurl_lst):
        count = 1
        for url in picurl_lst:
            res = requests.get(url)
            path = os.path.join(self.base_dir, '{}.png'.format(count))
            with open(path, 'wb') as f:
                f.write(res.content)
            count += 1

    def parse_page(self, source):
        soup = BeautifulSoup(source, 'lxml')
        # 获取标题
        title = soup.find('h1', class_='reader_ab_test with-top-banner')
        title = title.find('span').get_text()
        file_name = title + '.txt'
        # 获取内容
        doc_items = soup.select('.reader-txt-layer .ie-fix')
        content_lst = []
        for item in doc_items:
            for p in item.find_all('p'):
                content_lst.append(p.string)
        # 获取文档中所有图片
        picurl_lst = []
        pic_items = soup.select('.reader-pic-layer .ie-fix .reader-pic-item')
        try:
            for item in pic_items:
                img = item.find('img')
                url = img['src']
                picurl_lst.append(url)
        except:
            for item in pic_items:
                url = item['style']
                try:
                    url = re.search(r'url\((.*?)\)', url, re.S).group(1)
                    picurl_lst.append(url)
                except:
                    pass
        return file_name, picurl_lst, ''.join(content_lst).replace('\xa0', '')

    def run(self, url):
        try:
            self.browser.get(url)
            self.get_all_doc()
            file_name, picurl_lst, data = self.parse_page(
                self.browser.page_source)
            self.save_to_txt(file_name, data)
            self.save_all_picture(picurl_lst)
        except Exception as e:
            print(e.args)
        finally:
            self.browser.quit()


if __name__ == '__main__':
    url = 'https://wenku.baidu.com/view/a894bb23af45b307e87197fa.html'
    spider = BaiduDoc()
    spider.run(url)
