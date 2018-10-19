# -*- coding: utf-8 -*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

"""
金斧子净值采集脚本(动态获取cookie)
"""

import scrapy
import re
import pandas as pd
import requests
import time
import datetime as dt
import json
from fund_spider.pipelines import engine_private
from fund_spider.items import FundNvDataItem
from util.check_item import Check_item
from datetime import timedelta

CRAWL_ALL = (dt.date.today().day == 1 or dt.date.today().day == 16)


def login():
    session = requests.session()
    url = 'https://passport.jinfuzi.com/passport/user/doLogin.html'
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'

    # 金斧子账号   备用：18939862542 pwd： 68125542
    data = {"LoginForm[username]": "18891942195", "LoginForm[password]": "wp19950530."}

    headers = session.post(url, data=data, allow_redirects=False).headers['Location']
    if 'jfz' not in headers:
        time.sleep(10)
        headers = session.post(url, data=data, allow_redirects=False).headers['Location']
    if headers != '':
        headers = session.get(headers.replace('http:', 'https:'), allow_redirects=False).headers
        # try:
        #     PHPSESSID = re.search('PHPSESSID=(.+?);', headers['Set-Cookie'], re.DOTALL).group(1)
        # except KeyError:
        #     PHPSESSID = "c2oocsc13a8bc4410mmfrkgei2"
        if headers.get('Set-Cookie'):
            PHPSESSID = re.search('PHPSESSID=(.+?);', headers.get('Set-Cookie'), re.DOTALL)
            accessToken = re.search('accessToken=(.+?);', headers.get('Set-Cookie'), re.DOTALL)
            if PHPSESSID and accessToken:
                PHPSESSID = PHPSESSID.group(1)
                accessToken = accessToken.group(1)
                key_word = {'PHPSESSID': PHPSESSID, 'accessToken': accessToken}
                return key_word


class JFZNspider(scrapy.Spider):
    name = "jfz_fund_nv_new_spider"
    allowed_domains = ['www.jfz.com']
    # test = ('http://www.jfz.com/simu/list.html', 'http://www.jfz.com/simu/list.html')
    # start_urls = ('http://www.jfz.com/simu/list.html',)

    custom_settings = {'COOKIES_ENABLED': True,  # 登陆后才显示净值数据
                       'DOWNLOAD_DELAY': 3,

                       'DOWNLOADER_MIDDLEWARES': {
                           'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
                           'fund_spider.middlewares.RandomUserAgent.RandomUserAgent': 100,
                           'scrapy.downloadermiddlewares.retry.RetryMiddleware': 110,
                           # 'fund_spider.middlewares.RandomProxy.JFZProxy': 150,
                           'fund_spider.middlewares.middleware.JFZLoginmiddleware': 160,
                           # 'scrapy_splash.SplashMiddleware': 723,
                           # 'scrapy_splash.SplashCookiesMiddleware': 725,
                           # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
                       },
                       # 'SPIDER_MIDDLEWARES': {
                       #  'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
                       #  },
                       # # 设置Splash自己的去重过滤器
                       #  'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
                       #  # 缓存后台存储介质
                       #  'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage',
    }
    splash_url = "115.159.45.233:8050"

    # cookies = {
    #     "JRECORD_UID": "99c333bfebf8cccc7de643f9b4b5bfee",
    #     "JRECORD_FTIME": "1510032178",
    #     "gr_user_id": "80fa524d-12ed-403d-8cb4-4c1071123cc0",
    #     "isChecked": "true",
    #     "MY_HTTP_REFERER": "https%3A%2F%2Fwww.jfz.com%2Fsimu%2Flist.html",
    #     "JRECORD_LANDPAGE": "https%3A%2F%2Fwww.jfz.com%2Fsimu%2Fp-P61lo7lwan.html",
    #     "Hm_lvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1510724454,1513044571",
    #     "Hm_lpvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1513154734",
    #     "JRECORD_LTIME": "1513151536",
    #     "JRECORD_CTIME": "1513154734",
    #     "_smt_uid": "5a014331.3fe71479",
    #     "gr_session_id_9907c51ef09823c8d5b98c511e30a866": "67c2def5-9ce0-4294-9a26-70fa38cd0042",
    #     "gr_cs1_e7d2fff8 - 06e9 - 45d3 - 8979 - fa5802a36a4e": "user_id%3A4295813368",
    #     "compare_index": "0%26%261%26%262%26%263",
    #     # "PHPSESSID": "t5n335vvmch7mp7j89ipin2l55",
    #     "PHPSESSID": login(),
    #     "jfzWebUser": "966be85be230eb3fe4b85011fae4fd11486de158a%3A4%3A%7Bi%3A0%3Bs%3A10%3A%224295813368%22%3Bi%3A1%3Bs%3A11%3A%2218301806159%22%3Bi%3A2%3Bi%3A86400%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D",
    #     "jfz_login_id": "4295813368",
    #     "jfz_user_type": "0"
    # }
    # cookies = {
    #        "authTag": "18301806159",
    #        " JRECORD_UID": "399ba238f6b7952806e55458eeca8d63",
    #        " JRECORD_FTIME": "1528358393",
    #        " JRECORD_LTIME": "1528358393",
    #        " JRECORD_SRC": "https%3A%2F%2Fwww.google.com%2F",
    #        " JRECORD_LANDPAGE": "https%3A%2F%2Fwww.jfz.com%2F",
    #        " Hm_lvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1528358393",
    #        " _smt_uid": "5b18e5f9.4272b6a1",
    #        " gr_user_id": "21c110a7-91f2-43ee-bc2f-b5acc4c05c69",
    #        " gr_session_id_9907c51ef09823c8d5b98c511e30a866": "a1fcd803-8684-44cb-a93f-aefda314034d_true",
    #        " MEIQIA_EXTRA_TRACK_ID": "15gGak1J8rob8FwxgjW3lQDJ1Bs",
    #        " PHPSESSID": login(),
    #        " jfzWebUser": "27e4416ede2f9c601bbb3f7db1c04551221bd374a%3A4%3A%7Bi%3A0%3Bs%3A10%3A%224295813368%22%3Bi%3A1%3Bs%3A11%3A%2218301806159%22%3Bi%3A2%3Bi%3A86400%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D",
    #        " jfz_login_id": "4295813368",
    #        " accessToken": "d3965c15c9828311eee5bb3970056079",
    #        " jfz_user_type": "0",
    #        " authTag": "18301806159",
    #        " MY_HTTP_REFERER": "https%3A%2F%2Fwww.jfz.com%2Fsale%2Fsimu.html",
    #        " compare_index": "0%26%261%26%262%26%263",
    #        " JRECORD_CTIME": "1528358482",
    #        " Hm_lpvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1528358482"
    # }
    cookies = {
        "authTag": "18891942195",
        " JRECORD_UID": "399ba238f6b7952806e55458eeca8d63",
        " JRECORD_FTIME": "1528358393",
        " JRECORD_SRC": "https%3A%2F%2Fwww.google.com%2F",
        " _smt_uid": "5b18e5f9.4272b6a1",
        " gr_user_id": "21c110a7-91f2-43ee-bc2f-b5acc4c05c69",
        " MEIQIA_EXTRA_TRACK_ID": "15gGak1J8rob8FwxgjW3lQDJ1Bs",
        " MY_HTTP_REFERER": "https%3A%2F%2Fwww.jfz.com%2Fsale%2Fsimu.html",
        " compare_index": "0%26%261%26%262%26%263",
        " JRECORD_LTIME": "1528939392",
        " gr_cs1_46900fdf-7834-4965-bf17-96078f3714c3": "user_id%3A4295813368",
        " JRECORD_LANDPAGE": "https%3A%2F%2Fwww.jfz.com%2F",
        " Hm_lvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1528358393,1528959890,1528959894",
        " isChecked": "true",
        # " PHPSESSID": login(),
        " jfzWebUser": "6dc1320d8bbfe432569ce69ed7628e4bc9723be0a%3A4%3A%7Bi%3A0%3Bs%3A10%3A%223191812746%22%3Bi%3A1%3Bs%3A11%3A%2218891942195%22%3Bi%3A2%3Bi%3A86400%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D",
        " jfz_login_id": "3191812746",
        # " accessToken": "1c02b1c0d004c9b9641ae5622b254588",
        " jfz_user_type": "0",
        " gr_cs1_0683a085-8f58-4d14-b27d-28fe3fd52eb2": "user_id%3A3191812746",
        " gr_session_id_9907c51ef09823c8d5b98c511e30a866": "0683a085-8f58-4d14-b27d-28fe3fd52eb2_true",
        " authTag": "18891942195",
        " JRECORD_CTIME": "1528960455",
        " Hm_lpvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1528960455"
    }
    key_word = login()
    if key_word:
        cookies.update(key_word)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}

    def __init__(self, name=None, **kwargs):
        super(JFZNspider, self).__init__(name=None, **kwargs)
        # sql = 'SELECT jfz_id FROM __id_search WHERE priority >= "%s"' % datetime.today().day % 15
        # sql = 'SELECT jfz_id FROM __id_search '
        # 改为采集一年之内更新的金斧子id，缩小采集范围。
        year = timedelta(days=365)
        # sql = "SELECT jfz_id from __id_search where jfz_id  in ( SELECT * FROM (SELECT fund_id FROM d_fund_nv WHERE statistic_date > '%s' AND source_id='020002'ORDER BY statistic_date DESC ) AS T GROUP BY T.fund_id)" % (dt.datetime.strftime(dt.datetime.now()-year, "%Y-%m-%d"))
        sql = "select * from (SELECT fund_id from __id_search where source_id='020002' and fund_id  in  \
                ( SELECT * FROM (SELECT fund_id FROM d_fund_nv WHERE statistic_date > '%s' and source_id='020002' \
                ORDER BY statistic_date DESC ) AS T GROUP  BY T.fund_id)) as t1 \
                UNION (SELECT fund_id FROM __id_search WHERE source_id='020002' and fund_id NOT in (SELECT fund_id FROM d_fund_info WHERE source_id='020002') and entry_time>'2017-12-01')" % (dt.datetime.strftime(dt.datetime.now()-year, "%Y-%m-%d"))
        self.df = pd.read_sql(sql, engine_private, index_col='fund_id')
        self.index = self.df.index
        sql1 = "SELECT fund_id from __id_search WHERE source_id='020002'"
        self.df1 = pd.read_sql(sql1, engine_private, index_col='fund_id')
        self.index1 = self.df1.index
        # 单位出现错误，净值超过2000，页面不存在，只能从api中抓取
        # self.wrong_id = ['222227OC', '22222X37', 'P61ykxmbak', 'P61ykxmbwl', 'P61ykxmcg5',
        #                  'P61ykxmcio', 'P61ykxmcku', 'P61yml5not', 'P61yml5nt2', 'P61yml5o0p',
        #                  'P61yml5oci', 'P61yml5oj1', 'P61yml5oj7', 'P61yml5ojw', 'P61yml5orv',
        #                  'P61yml5p0e', 'P61yml5pb4', 'P61yml5qm3', 'P61yml5qm7', 'P61yml5qmk',
        #                  'P61yml5qmm', 'P6du9yzdlb', 'P6du9yzdlc']
        # api中曾经采集到，现在只能采集到部分得id
        # self._id = ["P61yml5qmm","P61yml5not"
        #                 "P61yml5qm3","P61yml5qm7","P6du9yzdlb","P6du9yzdlc"]
    # def _splash(self, url):
        # return "http://%s/render.html?url=%s&timeout=10&wait=5" % (self.splash_url, url)

    # def login(self):
    #     session = requests.Session()
    #     url = 'https://passport.jinfuzi.com/passport/user/doLogin.html'
    #     session.headers[
    #         'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    #
    #     # 金斧子账号   备用：18939862542 pwd： 68125542
    #     data = {"LoginForm[username]": "18301806159", "LoginForm[password]": "5461wen"}
    #
    #     headers = session.post(url,
    #                            data=data,
    #                            allow_redirects=False).headers['Location']
    #     if 'jfz' not in headers:
    #         time.sleep(10)
    #         headers = session.post(url,
    #                                data=data,
    #                                allow_redirects=False).headers['Location']
    #     headers = session.get(headers.replace('http:', 'https:'), allow_redirects=False).headers
    #     PHPSESSID = re.search('PHPSESSID = (. +?);', str(headers)).group(1)
    #     self.cookies['PHPSESSID'] = PHPSESSID
    #     # self.cookies = {'PHPSESSID': re.search('PHPSESSID=(.+?);', str(headers)).group(1), 'isChecked': 'true'}
    #     # self.log('%s获取到的session为： %s' % (datetime.now(), self.cookies['PHPSESSID']))
    def _refresh_cookie(self):
        new_phpsessid = login()
        # self.cookies.update({"PHPSESSID": new_phpsessid})
        self.cookies.update(new_phpsessid)

    def start_requests(self):
        # self.cookies = {}
        # fids = sorted(self.index.tolist())
        # for i in range(2500, len(fids), 100):
        #     print "从第%s进行抓取" % i
        #     for fund_id in fids[i:i+100]:
                # url = 'https://www.jfz.com/simu/p-%s.html' % fund_id
                # #     url = 'https://www.jfz.com/simu/p-22221BZS.html'
                # fund_id = '222293L8'
        # if CRAWL_ALL:
        #     for fund_id in set(self.index1):
        #         url = 'https://www.jfz.com/simu/simuProductNew/GetPrdNetWorthDrawDown?prdCode=%s' % fund_id
        #         # url = 'https://www.jfz.com/simu/simuProductNew/GetPrdNetWorthDrawDown?prdCode=22221Y2D'
        #         # fund_id = '22221Y2D'
        #         yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_history_navs,
        #                              meta={'fund_id': fund_id, 'retry': 0}, headers=self.headers)

        for fund_id in set(self.index):
            # fund_id = "22229T3E"
            # fund_name = "九坤CTA专享3号"
            url = 'https://www.jfz.com/simu/simuProductNew/GetPrdNetWorthDrawDown?prdCode=%s' % fund_id
            # url = 'https://www.jfz.com/simu/simuProductNew/GetPrdNetWorthDrawDown?prdCode=2222968J'
            # fund_id = '2222968J'
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_history_navs, meta={'fund_id': fund_id, 'retry': 0}, headers=self.headers)

    def parse_history_navs(self, response):
        datas = json.loads(response.body)
        check_login = datas[2].get("isLogin")
        infos = datas[2].get("hcData")
        if infos:
            if check_login is False and response.meta['retry'] < 2:
                self.log("cookie可能失效，刷新cookie")
                # print '%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1)
                sql = 'UPDATE  `__id_search` SET failed_request = failed_request + 1 WHERE fund_id = "%s"' % response.meta['fund_id']
                engine_private.execute(sql)
                self._refresh_cookie()
                yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse_history_navs,
                                     meta={'fund_id': response.meta['fund_id'], 'retry': response.meta['retry'] + 1},
                                     dont_filter=True, headers=self.headers)
            elif response.meta['retry'] >= 2:
                pass
            else:
                for info in infos:
                    item = FundNvDataItem()
                    item['fund_id'] = response.meta['fund_id']
                    # item['fund_name'] = self.df.at[response.meta['fund_id'], "fund_name"]
                    item['statistic_date'] = dt.datetime.fromtimestamp(float(info.get("x"))/1000)
                    item['nav'] = info.get("unitNet")
                    item['added_nav'] = info.get("accNet")
                    if float(item['nav']) > 2000:
                        item['nav'] = float(item['nav']) / 100
                        item['added_nav'] = float(item['added_nav']) / 100
                    item['data_source'] = 4
                    yield Check_item.check_item(item)




