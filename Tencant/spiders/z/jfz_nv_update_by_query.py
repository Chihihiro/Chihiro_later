# -*- coding: utf-8 -*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

"""
金斧子
"""

import scrapy
import re
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from fund_spider.zyyx_xiamen_refer import engine_test
from fund_spider.items import FundNvDataItem, FundInfoItem
from util.date_convert import GetNowTime, regularize_time
from util.to_sql import to_sql


class JFZNspider(scrapy.Spider):
    """改版后只能根据已有id查询更新"""
    name = "jfz_nv_query_spider"
    allowed_domains = ['www.jfz.com']
    test = ('http://www.jfz.com/simu/list.html', 'http://www.jfz.com/simu/list.html')
    start_urls = ('http://www.jfz.com/simu/list.html',)
    #
    # custom_settings = {
    #     'REDIRECT_ENABLED': False,
    #     'AUTOTHROTTLE_ENABLED': False,
    #     'CONCURRENT_REQUESTS_PER_DOMAIN': 80,  #对单个网站进行并发请求的最大值。
    #     'CONCURRENT_REQUESTS': 80,              #Scrapy downloader 并发请求(concurrent requests)的最大值
    #     'DOWNLOAD_DELAY': 0.5,
    #     'DOWNLOAD_TIMEOUT':50,                #如果使用代理，超时时间要设定的相对较长
    #     'RETRY_ENABLED': True,
    #     'RETRY_TIMES': 50,
    #     'RETRY_HTTP_CODES': [301, 302, 303,502,503,504,500,403,404,401,400,408,407,307], #不设置  第二次尝试会被去重去掉
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    #         'fund_spider.middlewares.RandomUserAgent.RandomUserAgent': 100,
    #         'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 110,
    #         'fund_spider.middlewares.RandomProxy.JFZProxy': 150,
    #         'fund_spider.middlewares.middleware.JFZLoginmiddleware': 160,
    #     },
    #     'COOKIES_ENABLED':True  #登陆后才显示净值数据
    # }
    custom_settings = {'COOKIES_ENABLED': True,  # 登陆后才显示净值数据
                       'DOWNLOADER_MIDDLEWARES': {
                           'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
                           'fund_spider.middlewares.RandomUserAgent.RandomUserAgent': 100,
                           'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
                           'fund_spider.middlewares.middleware.JFZLoginmiddleware': 160
                       },

                       }

    def __init__(self, name=None, **kwargs):
        super(JFZNspider, self).__init__(name=None, **kwargs)
        sql = 'SELECT fund_id, fund_name, statistic_date, delta, crawl_schedule, data_source, crawl_times, get_new_times ' \
              'FROM dynamic_update WHERE data_source=4 and statistic_date>"2017-06-01" and crawl_schedule<= current_date() ' \
              'and id_abandoned is null'
        self.df = pd.read_sql(sql, engine_test, index_col='fund_id')
        self.df = self.df.loc[self.df['statistic_date'].map(lambda x: x is not None)]
        self.df['statistic_date'] = self.df['statistic_date'].map(lambda x: x.__str__()[0:10])
        # self.df['statistic_date'] = '1980-01-01'
        self.index = self.df.index
        self.date = datetime.now()
        self.session = sessionmaker(bind=engine_test)()

    def login(self):
        session = requests.Session()
        url = 'https://passport.jinfuzi.com/passport/user/doLogin.html'
        session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

        # 金斧子账号   备用：18939862542 pwd： 68125542
        data = {"LoginForm[username]": "13918463228", "LoginForm[password]": "azul1846"}

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
        for fund_id in self.index[0:1]:  # 长度只能为1
            url = 'https://www.jfz.com/product/%s.html' % fund_id
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse,
                                 meta={'dont_redirect': True})

    def parse(self, response):
        for fund_id in self.index:
            url = 'https://www.jfz.com/product/%s.html' % fund_id
            update = self.df.get_value(fund_id, 'statistic_date')
            fund_name = self.df.get_value(fund_id, 'fund_name')  # 名字从库中获取，但存在网站同编码不同基金的极小可能
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_history_navs,
                                 meta={'retry': 0, 'update': update, 'fund_id': fund_id, 'fund_name': fund_name,
                                       'dont_redirect': True})

    def parse_history_navs(self, response):
        self.log(response.url)
        datas = re.search('<!--start历史净值表-->(.*?)<!--end历史净值表-->', response.body, re.DOTALL)
        if response.body == 'id_abandoned':
            fund_id = response.url.replace('https://www.jfz.com/product/', '').replace('.html', '')
            df = self.df.loc[[fund_id, ]]
            df['crawl_times'] = df['crawl_times'].map(lambda x: x + 1)
            df['id_abandoned'] = 1
            df.reset_index(inplace=True)
            to_sql('dynamic_update', self.session, df, type="update")

        elif not datas and response.meta['retry'] < 2:
            self.log('%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1))
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse_history_navs,
                                 meta={'fund_name': response.meta['fund_name'], 'dont_redirect': True,
                                       'fund_id': response.meta['fund_id'], 'retry': response.meta['retry'] + 1},
                                 dont_filter=True)
        else:
            records = re.findall('<tr class=(.*?)</tr>', datas.group(1), re.DOTALL)
            flag = 0
            global date, nav
            for record in records[0:]:
                infos = re.search(
                    '<td width="28%" class="tl">(.*?)</td>\s+<td width="">(.*?)</td>\s+<td width="">(.*?)</td>', record,
                    re.DOTALL)
                statistic_date = regularize_time(infos.group(1))
                if statistic_date > response.meta['update']:
                    item = FundNvDataItem()
                    item['fund_id'] = response.meta['fund_id']
                    item['fund_name'] = response.meta['fund_name']
                    # item['reg_code'] = reg_code
                    item['nav'] = infos.group(2)
                    item['sanav'] = infos.group(3)
                    item['statistic_date'] = regularize_time(infos.group(1))
                    # item['entry_time'] = GetNowTime()
                    item['source_code'] = 3
                    item['data_source'] = 4
                    item['data_source_name'] = '金斧子'
                    # print item
                    if item['nav'][0] in '0123456789':
                        if not flag:
                            date = item['statistic_date']
                            nav = item['nav']
                        flag = 1
                        yield item
                else:
                    self.log('%s 已更新到最新' % response.meta['fund_id'])
                    break

            df = self.df.loc[[response.meta['fund_id'], ]]
            df['delta'] = df['delta'].map(lambda x: 1 if flag else x + 1)
            df['statistic_date'] = date if flag else df['statistic_date']
            df['crawl_times'] = df['crawl_times'].map(lambda x: x + 1)
            df['get_new_times'] = df['get_new_times'].map(lambda x: x + 1 if flag else x)
            df['crawl_schedule'] = df['delta'].map(lambda x: str(self.date + timedelta(x))[0:10])
            df.reset_index(inplace=True)
            to_sql('dynamic_update', self.session, df, type="update")
