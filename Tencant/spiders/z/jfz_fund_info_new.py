# -*- coding: utf-8 -*-
# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf-8')

"""
金斧子临时info抓取脚本，api

"""

import scrapy
import re
import datetime as dt
import pandas as pd
from fund_spider.pipelines import engine_private
from fund_spider.items import FundInfoItem
from datetime import timedelta


CRAWL_ALL = (dt.date.today().day == 6)


class JFZtemplate(scrapy.Spider):
    name = "jfz_fund_info_new_spider"
    allowed_domains = ['www.jfz.com']
    version = dt.datetime.today().strftime("%Y%m%d%H")
    custom_settings = {'COOKIES_ENABLED': True,
                       }
    cookies = {
        "JRECORD_UID": "99c333bfebf8cccc7de643f9b4b5bfee",
        "JRECORD_FTIME": "1510032178",
        "gr_user_id": "80fa524d-12ed-403d-8cb4-4c1071123cc0",
        "isChecked": "true",
        "JRECORD_LANDPAGE": "https % 3A % 2F % 2Fwww.jfz.com % 2Fproduct % 2F22221684.html",
        "Hm_lvt_9cfdc8c0bb3c0ab683956289eef9f34a": "1513044571",
        "JRECORD_LTIME": "1510032178",
        "JRECORD_CTIME": "1513820641",
        "_smt_uid": "5a014331.3fe71479",
        "gr_session_id_9907c51ef09823c8d5b98c511e30a866": "6796a21f-ce7a-41ed-be65-c88762216860",
        "gr_cs1_e7d2fff8 - 06e9 - 45d3 - 8979 - fa5802a36a4e": "user_id % 3A6176844059",
        "compare_index": "0 % 26 % 261 % 26 % 262 % 26 % 263",
        "PHPSESSID": "estn1u60jf2fupe0rn1son3tm7",
        "jfzWebUser": "3beb5cec21b92abe7eba9fcb9cccf7c31af51a10a % 3A4 % 3A % 7Bi % 3A0 % 3Bs % 3A10 % 3A % 226176844059 % 22 % 3Bi % 3A1 % 3Bs % 3A11 % 3A % 2215026588463 % 22 % 3Bi % 3A2 % 3% 3A86400 % 3% 3% 3Ba % 3A0 % 3A % 7B % 7D % 7D",
        "jfz_login_id": "6176844059",
        "jfz_user_type": "0"
    }
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
        super(JFZtemplate, self).__init__(name=None, **kwargs)
        # year = timedelta(days=365)
        # sql = "SELECT jfz_id from __id_search where jfz_id  in ( SELECT * FROM (SELECT fund_id FROM d_fund_nv WHERE statistic_date > '%s' AND source_id='020002'ORDER BY statistic_date DESC ) AS T GROUP BY T.fund_id)" % (dt.datetime.strftime(dt.datetime.now()-year, "%Y-%m-%d"))
        sql ="SELECT fund_id FROM __id_search WHERE fund_id NOT in (SELECT fund_id FROM d_fund_info WHERE source_id='020002') and entry_time>'2017-12-01' and source_id='020002'"
        self.df = pd.read_sql(sql, engine_private, index_col='fund_id')
        self.index = self.df.index
        sql1 = "SELECT fund_id from __id_search WHERE source_id='020002'"
        self.df1 = pd.read_sql(sql1, engine_private, index_col='fund_id')
        self.index1 = self.df1.index

    def start_requests(self):
        if CRAWL_ALL:
            for fund_id in set(self.index1):
                    # url = 'https://www.jfz.com/simu/p-P62clcj5u9.html'
                    # fund_id = 'P62clcj5u9'
                url = "https://www.jfz.com/simu/p-%s.html" % fund_id
                yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse,
                                     meta={'fund_id': fund_id, 'retry': 0}, )
        else:
            for fund_id in set(self.index):
                url = "https://www.jfz.com/simu/p-%s.html" % fund_id
                yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse,
                                     meta={'fund_id': fund_id, 'retry': 0}, )
        # lis = [
        #     'P61hb3jtm3',
        #     'P61l2pmauh',
        #     'P61l2pmav2',
        #     'P61l60p1w1'
        # ]
        # for fund_id in lis:
        #     url = "https://www.jfz.com/simu/p-%s.html" % fund_id
        #     yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse,
        #                     meta={'fund_id': fund_id, 'retry': 0}, )

    def parse(self, response):
        reg_code_a = response.xpath('.//ul[@class="basic clearfix"]//li[5]//span[@class="content"]/a')
        manager_a = response.xpath('.//ul[@class="basic clearfix"]//li[3]//span[@class="content"]/a')
        fund_name = response.xpath('//h1[@class="caption"]/text()').extract()
        if fund_name:
            fund_name = fund_name[0]
        if reg_code_a:
            reg_code = reg_code_a.xpath('./text()').extract()[0]
        else:
            reg_code = response.xpath('.//ul[@class="basic clearfix"]//li[5]//span[@class="content"]/text()').extract()[
                0]
        if manager_a:
            manager = manager_a.xpath('./text()').extract()[0]
        else:
            manager = response.xpath('.//ul[@class="basic clearfix"]//li[3]//span[@class="content"]/text()').extract()[
                0]
        url = 'https://www.jfz.com/simu/simuProductNew/getprdinfomation?prdCode=%s' % response.meta['fund_id']
        yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_info,
                             meta={'reg_code': reg_code, 'manager': manager, 'fund_id': response.meta['fund_id'], 'fund_name': fund_name})

    def parse_info(self, response):
        info_dict = {
            "prdFullName": "fund_full_name",
            "buildDate": "foundation_date",
            "prdState": "fund_status",
            "bankName": "fund_custodian",
            "comFullName": "fund_manager_nominal",
            "fundPrdType": "fund_type_issuance",
            "openRemark": "open_date",
            "closeRemark": "locked_time_limit",
            "fundType": "type_name",
            "substrategy": "stype_name",
            "minCap": "min_purchase_amount",
            "comName": "fund_manager",
            "feeFixed": "fee_manage",  # 管理费率
            "feeRedem": "fee_redeem",  # 赎回费率
            "feePurch": "fee_subscription",  # 认购费率
            "feeFloat": "fee_pay",  # 业绩报酬
        }
        item = FundInfoItem()
        for key in info_dict.keys():
            value = re.search('"{}":"(.+?)",'.format(key), response.body, re.DOTALL)
            if value:
                item[info_dict[key]] = value.group(1).decode('unicode_escape')
        item['fund_id'] = response.meta['fund_id']
        item['fund_name'] = response.meta['fund_name']
        item['reg_code'] = response.meta['reg_code']
        item['fund_member'] = response.meta['manager']
        item['data_source'] = 4
        item['version'] = self.version
        yield item
