# -*- coding: utf-8 -*-
# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf-8')

"""
金斧子
"""

import scrapy
import re
import requests
import time
from datetime import datetime
from util.str_clean import clean_str_strong
from fund_spider.items import dFundPersonDpItem
class JFZPDspider(scrapy.Spider):
    name = "jfz_person_desc_spider"
    allowed_domains = ['www.jfz.com']
    start_urls = ('http://www.jfz.com/simu/manager.html',)
    custom_settings = {
        'COOKIES_ENABLED': True,  # 登陆后才显示净值数据

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'fund_spider.middlewares.RandomUserAgent.RandomUserAgent': 100,
            'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 110,
            # 'fund_spider.middlewares.RandomProxy.JFZProxy': 150,
            'fund_spider.middlewares.middleware.JFZLoginmiddleware': 160
        },

    }

    def login(self):
        session = requests.Session()
        url = 'https://passport.jinfuzi.com/passport/user/doLogin.html'
        session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

        # 金斧子账号  备用：18939862542 pwd： 68125542
        data = {"LoginForm[username]": "15026588463", "LoginForm[password]": "68125542"}
        headers = session.post(url,
                               data=data,
                               allow_redirects=False).headers['Location']
        if 'jfz' not in headers:
            time.sleep(10)
            headers = session.post(url,
                                   data=data,
                                   allow_redirects=False).headers['Location']
        headers = session.get(headers.replace('http:', 'https:'), allow_redirects=False).headers
        self.cookies = {'PHPSESSID': re.search('PHPSESSID=(.+?);', str(headers)).group(1), 'isChecked': 'true'}
        self.log('%s获取到的session为： %s' % (datetime.now(), self.cookies['PHPSESSID']))

    def start_requests(self):
        self.cookies = {}
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_pages,
                                 meta={'retry': 0})

    def parse_pages(self, response):
        max_page_num = re.search('<li class="page-item page-last">\s*?<a href="(.*?)"></a></li>', response.body).group(1)
        max_page_num = int(re.search('\d+', max_page_num).group(0))
        self.log(max_page_num)
        for i in range(1, max_page_num + 1):
            url = 'https://www.jfz.com/simu/manager_p%d.html' % i
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_person, meta={'retry': 0},
                                 dont_filter=True)

    def parse_person(self, response):
        self.log(response.url)
        records = re.findall('<td class="t-manager">(.*?)咨询</a>', response.body, re.DOTALL)
        if not records and response.meta['retry'] < 2:
            print('%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1))
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse,
                                 meta={'flag': response.meta['flag'], 'retry': response.meta['retry'] + 1},
                                 dont_filter=True)
        for record in records:
            person_name = clean_str_strong(re.search('<a href="/simu/m-(.*?).html" target="_blank">(.*?)</a>', record, re.DOTALL).group(2))
            person_id = re.search('<a href="/simu/m-(.*?).html" target="_blank">(.*?)</a>', record, re.DOTALL).group(1)
            url = 'https://www.jfz.com/simu/m-%s.html' % person_id
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_info,
                                 meta={'person_name': person_name, 'person_id': person_id, 'retry': 0}, dont_filter=True)

    def parse_info(self, response):
        self.log(response.url)
        item = dFundPersonDpItem()
        item["person_id"] = response.meta["person_id"]
        item["person_name"] = response.meta["person_name"]
        item["source_id"] = '020002'
        item["resume"] = "".join(response.xpath('//div[@class="mgr_con"]//text()').extract()) if " " else "".join(response.xpath('//div[@class="tab_con_txt"]//text()').extract())
        yield item