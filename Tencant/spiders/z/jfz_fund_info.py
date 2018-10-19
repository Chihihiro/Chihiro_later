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
import pandas as pd
from fund_spider.zyyx_xiamen_refer import engine_crawl
from fund_spider.items import FundNvDataItem, FundInfoItem
from util.date_convert import GetNowTime, regularize_time


class JFZIspider(scrapy.Spider):
    name = "jfz_fund_info_spider"
    allowed_domains = ['www.jfz.com']
    start_urls = ('http://www.jfz.com/simu/list.html',)
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
    info_dict = {
        '基金全称': 'fund_full_name',
        '成立时间': 'foundation_date',
        '基金状态': 'fund_status',
        '管理人': 'fund_manager_nominal',
        '投资顾问': 'fund_manager',
        '投资策略': 'type_name',
        '投资子策略': 'stype_name',
        '基金类型': 'fund_type_issuance',
        '托管机构': 'fund_custodian',
        '开放日期': 'open_date',
        '封闭期长': 'locked_time_limit',
        '认购起点': 'min_purchase_amount',
        '认购费率': 'fee_subscription',
        '管理费率': 'fee_manage',
        '赎回费率': 'fee_redeem',
        '业绩报酬': 'fee_pay',
        '备案编号': 'reg_code'
    }

    def __init__(self, name=None, **kwargs):
        super(JFZIspider, self).__init__(name=None, **kwargs)
        sql = 'SELECT DISTINCT fund_id FROM d_fund_info WHERE data_source=4 '
        self.df = pd.read_sql(sql, engine_crawl, index_col='fund_id')
        self.index = self.df.index

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
        self.log('%s获取到的session为： %s' % (datetime.now(), self.cookies['PHPSESSID']))  # 过期：1800s

    def start_requests(self):
        self.cookies = {}
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_pages,
                                 meta={'retry': 0})

    def parse_pages(self, response):
        max_page_num = re.search('<li class="page-item page-last">\s*?<a href="(.*?)"></a></li>', response.body).group(1)
        max_page_num = int(re.search('\d+', max_page_num).group(0))
        self.log(max_page_num)
        max_page_num = 100
        for i in range(1, max_page_num + 1):
            url = 'https://www.jfz.com/simu/list_p%d.html' % i
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_funds, meta={'retry': 0}, dont_filter=True)

    def parse_funds(self, response):
        records = re.findall('<td class="t-compare">(.*?)咨询</a>', response.body, re.DOTALL)
        if not records and response.meta['retry'] < 2:
            print('%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1))
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse,
                                 meta={'flag': response.meta['flag'], 'retry': response.meta['retry'] + 1},
                                 dont_filter=True)

        for record in records[0::]:
            fund_id = re.search('target="_blank" href="/product/(.*?).html"', record, re.DOTALL).group(1)
            if fund_id in self.index:
                self.log('%s 库中已存在， 不采集' % fund_id)
                continue
            self.log('%s 库中缺少， 采集' % fund_id)
            fund_name = re.search('<td class="t-name">\s*?<a title="(.*?)" target="_blank" href=', record,
                                  re.DOTALL).group(1)
            url = 'https://www.jfz.com/product/%s.html' % fund_id
            # print fund_id,fund_name
            if fund_id == '05P61l7o8dcu':
                continue
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_info,
                                 meta={'fund_name': fund_name, 'fund_id': fund_id, 'retry': 0}, dont_filter=True)

    def parse_info(self, response):
        self.log(response.url)
        trs = response.xpath('//div[@class="v4_simu_pro_basic clearfix"]//tr')
        item_info = FundInfoItem()
        flag = 0
        for i in self.info_dict.keys():
            for tr in trs:
                value = tr.xpath(u'./th[contains(text(),"%s")]/following-sibling::td/text()' % i).extract()
                if value:
                    item_info[self.info_dict[i]] = value[0].strip()
                    flag = 1
                    break
        if flag:
            item_info['fund_id'] = response.meta['fund_id']
            item_info['fund_name'] = response.meta['fund_name']
            item_info['data_source'] = 4
            item_info['data_source_name'] = '金斧子'
            item_info['foundation_date'] = regularize_time(item_info['foundation_date'])
            item_info['version'] = self.version
            # print item_info
            yield item_info
