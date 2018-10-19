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
from fund_spider.items import FundPersonItem, dPersonOrgItem, dPersonFundItem


class JFZPspider(scrapy.Spider):
    name = "jfz_person_info_spider"
    allowed_domains = ['www.jfz.com']
    start_urls = ('https://www.jfz.com/simu/manager.html',)
    version = datetime.today().strftime("%Y%m%d%H")
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
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse_person,
                                 meta={'retry': response.meta['retry'] + 1},
                                 dont_filter=True)
        for record in records:
            person_name = clean_str_strong(re.search('<a href="/simu/m-(.*?).html" target="_blank">(.*?)</a>', record, re.DOTALL).group(2)).strip()
            person_id = re.search('<a href="/simu/m-(.*?).html" target="_blank">(.*?)</a>', record, re.DOTALL).group(1)
            url = 'https://www.jfz.com/simu/m-%s.html' % person_id
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_info,
                                 meta={'person_name': person_name, 'person_id': person_id, 'retry': 0}, dont_filter=True)

    def parse_info(self, response):
        self.log(response.url)
        funds_num = response.xpath('//div[@class="detail_box_2"]//tr[2]//td//text()').extract()[0]
        org = response.xpath('//div[@class="detail_box_2"]//li[@class="attr_item attr_item_last"]//td[1]//text()').extract()[1]
        org_name = clean_str_strong(org)
        org_url = response.xpath('//div[@class="detail_box_2"]//li[@class="attr_item attr_item_last"]//td[1]//a//@href').extract()
        if org_url:
            org_url = org_url[0]
            org_id = re.findall('/simu/c-(.+?).html', org_url, re.DOTALL)[0]
        else:
            org_id = None
        background = response.xpath('//div[@class="detail_box_2"]//tr[3]//td//text()').extract()[2]
        investment_years = response.xpath(u'//descendant::th[text()="从业年限："]/following-sibling::td//text()').extract()[0]
        item = FundPersonItem()
        item['user_id'] = response.meta['person_id']
        item['user_name'] = response.meta['person_name']
        item['org_name'] = org_name
        item['duty'] = '基金经理'
        item['background'] = background
        item['investment_years'] = investment_years
        item['funds_num'] = funds_num
        item['data_source'] = 4
        item['data_source_name'] = '金斧子'
        item['version'] = self.version
        yield item
        item1 = dPersonOrgItem()
        item1['person_id'] = response.meta['person_id']
        item1['person_name'] = response.meta['person_name']
        item1['org_name'] = org_name
        item1['org_id'] = org_id
        item1['source_id'] = '020002'
        item1['is_current'] = 1
        item1['version'] = self.version
        yield item1
        trs2 = response.xpath('//div[@class="tab_con active"]//tr')
        for tr2 in trs2[1:]:
            if tr2:
                tr2 = tr2.extract()
                item3 = dPersonFundItem()
                item3['person_id'] = response.meta['person_id']
                item3['person_name'] = response.meta['person_name']
                item3['source_id'] = '020002'
                item3['fund_name'] = re.search('<a href="(.+?)" target="_blank" title="(.+?)">(.*?)</a>', tr2,
                                               re.DOTALL).group(2)
                item3['fund_id'] = re.search('<a href="/simu/p-(.*)\.html" target="_blank" ', tr2, re.DOTALL).group(1)
                item3['is_current'] = 1
                item3['version'] = self.version
                yield item3
        trs = response.xpath('//div[@class="tab_con"]//tr')
        for tr in trs[1:]:
            if tr:
                tr = tr.extract()
                item2 = dPersonFundItem()
                item2['person_id'] = response.meta['person_id']
                item2['person_name'] = response.meta['person_name']
                item2['source_id'] = '020002'
                item2['fund_name'] = re.search('<a href="(.+?)" target="_blank" title="(.+?)">(.*?)</a>', tr,
                                               re.DOTALL).group(2)
                item2['fund_id'] = re.search('<a href="/simu/p-(.*)\.html" target="_blank" ', tr, re.DOTALL).group(1)
                item2['is_current'] = 0
                item2['version'] = self.version
                yield item2
