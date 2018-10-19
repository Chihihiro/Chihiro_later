# -*- coding: utf-8 -*-
# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf-8')

"""
金斧子
从数据抓出fund_id直接插入到start_urls = ('http://www.jfz.com/simu/%s.html') % fund_id
"""

import scrapy
import re
import requests
import time
from util import to_sql
from datetime import datetime
import pandas as pd
from fund_spider.zyyx_xiamen_refer import engine_crawl
from fund_spider.pipelines import engine_private
from fund_spider.items import FundInfoItem
from util.date_convert import regularize_time


class JFZIspider(scrapy.Spider):
    name = "jfz_fund_info_whole_spider"
    allowed_domains = ['www.jfz.com']
    version = datetime.today().strftime("%Y%m%d%H")
    # start_urls = ('http://www.jfz.com/simu/list.html',)
    # start_urls = ('http://www.jfz.com/simu/.html',)
    custom_settings = {'COOKIES_ENABLED': True,  # 登陆后才显示净值数据

                       # 'DOWNLOADER_MIDDLEWARES': {
                       #     'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
                       #     'fund_spider.middlewares.RandomUserAgent.RandomUserAgent': 100,
                       #     'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 110,
                       #     # 'fund_spider.middlewares.RandomProxy.JFZProxy': 150,
                       #     'fund_spider.middlewares.middleware.JFZLoginmiddleware': 160
                       # },

                       }
    cookies = {
        "JRECORD_UID": "99c333bfebf8cccc7de643f9b4b5bfee",
        "JRECORD_FTIME": "1510032178",
        "gr_user_id": "80fa524d-12ed-403d-8cb4-4c1071123cc0",
        "isChecked": "true",
        "JRECORD_LANDPAGE": "https % 3A % 2F % 2Fwww.jfz.com % 2Fproduct % 2F22221684.html",
        "Hm_lvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1510032178, 1510724454",
        "Hm_lpvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1512032654",
        "JRECORD_LTIME": "1512029773",
        "JRECORD_CTIME": "1512032654",
        "_smt_uid": "5a014331.3fe71479",
        "gr_session_id_9907c51ef09823c8d5b98c511e30a866": "e7d2fff8 - 06e9 - 45d3 - 8979 - fa5802a36a4e",
        "gr_cs1_e7d2fff8 - 06e9 - 45d3 - 8979 - fa5802a36a4e": "user_id % 3A6176844059",
        "compare_index": "0 % 26 % 261 % 26 % 262 % 26 % 263",
        "PHPSESSID": "u3mbpsc4ir9qef4r0hpm97toe2",
        "jfzWebUser": "3beb5cec21b92abe7eba9fcb9cccf7c31af51a10a % 3A4 % 3A % 7Bi % 3A0 % 3Bs % 3A10 % 3A % 226176844059 % 22 % 3Bi % 3A1 % 3Bs % 3A11 % 3A % 2215026588463 % 22 % 3Bi % 3A2 % 3% 3A86400 % 3% 3% 3Ba % 3A0 % 3A % 7B % 7D % 7D",
        "jfz_login_id": "6176844059",
        "jfz_user_type": "0"
    }
    headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
    info_dict = {'基金全称': 'fund_full_name',
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
        sql = 'SELECT jfz_id FROM __id_search WHERE priority >= "%s"' % datetime.today().day % 15
        self.df = pd.read_sql(sql, engine_private, index_col='jfz_id')
        self.index = self.df.index

    # def login(self):
    #     session = requests.Session()
    #     url = 'https://passport.jinfuzi.com/passport/user/doLogin.html'
    #     session.headers[
    #         'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    #
    #     # 金斧子账号  备用：18939862542 pwd： 68125542
    #     data = {"LoginForm[username]": "15026588463", "LoginForm[password]": "68125542"}
    #     headers = session.post(url,
    #                            data=data,
    #                            allow_redirects=False).headers['Location']
    #     if 'jfz' not in headers:
    #         time.sleep(10)
    #         headers = session.post(url,
    #                                data=data,
    #                                allow_redirects=False).headers['Location']
    #     headers = session.get(headers.replace('http:', 'https:'), allow_redirects=False).headers
    #     self.cookies = {'PHPSESSID': re.search('PHPSESSID=(.+?);', str(headers)).group(1), 'isChecked': 'true'}
    #     self.log('%s获取到的session为： %s' % (datetime.now(), self.cookies['PHPSESSID']))  # 过期：1800s
    # def err(self, failture):

    def start_requests(self):
        for fund_id in set(self.index):
            url = 'https://www.jfz.com/simu/p-%s.html' % fund_id
            #     url = 'https://www.jfz.com/simu/p-22221BZS.html'
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_info, meta={'fund_id':fund_id, 'retry': 0}, headers=self.headers, )

    def parse_info(self, response):
        self.log(response.url)
        lis = response.xpath('//div[@class="profile"]//ul[@class="basic clearfix"]//li')
        if not lis and response.meta['retry'] < 2:
            print('%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1))
            sql = 'UPDATE  `__id_search` SET failed_request = failed_request + 1 WHERE jfz_id = "%s"' % response.meta['fund_id']
            engine_private.execute(sql)
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse_info, meta={'fund_id': response.meta['fund_id'], 'retry': response.meta['retry'] + 1}, dont_filter=True, headers=self.headers)

        item_info = FundInfoItem()
        flag = 0
        for i in self.info_dict.keys():
            for li in lis:
                value = li.xpath(u'./span[contains(text(),"%s")]/following-sibling::span/text()' % i).extract()
                if value:
                    item_info[self.info_dict[i]] = value[0].strip()
                    flag = 1
                    break
        if flag:
            item_info['fund_id'] = response.meta['fund_id']
            item_info['fund_name'] = response.xpath('//div[@class="profile"]//div[@class="header clearfix"]//h1[@class="caption"]/text()').extract()[0]
            item_info['data_source'] = 4
            item_info['data_source_name'] = '金斧子'
            item_info['foundation_date'] = regularize_time(item_info['foundation_date'])
            item_info['version'] = self.version
            # print item_info
            yield item_info
