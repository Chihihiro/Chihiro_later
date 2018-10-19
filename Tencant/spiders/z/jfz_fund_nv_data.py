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
from datetime import datetime
from fund_spider.zyyx_xiamen_refer import engine_crawl
from fund_spider.items import FundNvDataItem, FundInfoItem
from util.date_convert import regularize_time
from scrapy.exceptions import CloseSpider


class JFZNspider(scrapy.Spider):
    name = "jfz_fund_nv_data_spider"
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
                           'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 110,
                           # 'fund_spider.middlewares.RandomProxy.JFZProxy': 150,
                           'fund_spider.middlewares.middleware.JFZLoginmiddleware': 160
                       },

                       }

    def __init__(self, name=None, **kwargs):
        super(JFZNspider, self).__init__(name=None, **kwargs)
        sql = 'SELECT fund_id, MAX(statistic_date) as statistic_date  FROM d_fund_nv_data WHERE data_source=4 GROUP BY fund_id'
        self.df = pd.read_sql(sql, engine_crawl, index_col='fund_id')
        self.df = self.df.loc[self.df['statistic_date'].map(lambda x: x is not None)]
        self.df['statistic_date'] = self.df['statistic_date'].map(lambda x: x.__str__()[0:10])
        # self.df['statistic_date'] = '1980-01-01'
        self.index = self.df.index
        # print self.df

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
        for url in self.start_urls:  # self.start_urls长度只能为1， 登录方式决定的
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse,
                                 meta={'flag': 1, 'retry': 0})

    def parse(self, response):
        records = re.findall('<td class="t-compare">(.*?)咨询</a>', response.body, re.DOTALL)
        print(len(records))
        if len(re.findall('认证可见', response.body, re.DOTALL)) > 20:
            raise CloseSpider
        if not records and response.meta['retry'] < 2:
            print('%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1))
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse,
                                 meta={'flag': response.meta['flag'], 'retry': response.meta['retry'] + 1},
                                 dont_filter=True)

        for record in records[0::]:
            date_online = re.search('<span class="date">\((\d{2}-\d{2})\)</span>', record, re.DOTALL)
            if date_online:
                date_online = date_online.group(1)
                fund_id = re.search('target="_blank" href="/simu/p-(.*?).html"', record, re.DOTALL).group(1)
                fund_name = re.search('<td class="t-name">\s*?<a title="(.*?)" target="_blank" href=', record,
                                      re.DOTALL).group(1)
                # print fund_id, fund_name
                # if fund_id in self.index:
                #     update = self.df.get_value(fund_id, 'statistic_date')
                #     if update[5:10] >= date_online:
                #         self.log('%s库中: %s已经是最新，不采集' % (fund_id, update))
                #         continue
                #     else:
                #         self.log('%s库中: %s落后于最新: %s，采集' % (fund_id, update, date_online))
                # else:
                #     update = '1980-01-01'
                #     self.log('库中缺少%s: %s，新增' % (fund_id, fund_name))
                url = 'https://www.jfz.com/simu/p-%s.html' % fund_id
                yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_history_navs,
                                     meta={'fund_name': fund_name, 'fund_id': fund_id, 'retry': 0, 'update': update},
                                     dont_filter=True)
            else:
                continue
        if response.meta['flag']:
            page_num = re.search('<li class="page-item page-last">\s*?<a href="(.*?)"></a></li>', response.body).group(
                1)
            page_num = int(re.search('\d+', page_num).group(0))
            self.log(page_num)
            page_num = 3000 if page_num < 300 else page_num  # 2017-09-19前端只能看到100页
            for i in range(int(page_num * 0.999), 1, -1):  # 该网站会出现最后几页消失 且 不可访问的情况
                # for i in range(2, 1, -1):
                url = 'https://www.jfz.com/simu/list_p%d.html' % i
                yield scrapy.Request(url, cookies=self.cookies, callback=self.parse, meta={'flag': 0, 'retry': 0},
                                     dont_filter=True)

    def parse_history_navs(self, response):
        self.log(response.url)
        datas = re.search('<!--start历史净值表-->(.*?)<!--end历史净值表-->', response.body, re.DOTALL)
        if not datas and response.meta['retry'] < 2:
            print('%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1))
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse_history_navs,
                                 meta={'fund_name': response.meta['fund_name'], 'fund_id': response.meta['fund_id'],
                                       'retry': response.meta['retry'] + 1}, dont_filter=True)
        else:
            records = re.findall('<tr class=(.*?)</tr>', datas.group(1), re.DOTALL)
            for record in records[0:]:
                infos = re.search(
                    '<td width="28%" class="tl">(.*?)</td>\s+<td width="">(.*?)</td>\s+<td width="">(.*?)</td>', record,
                    re.DOTALL)
                statistic_date = regularize_time(infos.group(1))
                # if statistic_date > response.meta['update']:
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
                    yield item
                # else:
                #     self.log('%s 已更新到最新' % response.meta['fund_id'])
                #     break
