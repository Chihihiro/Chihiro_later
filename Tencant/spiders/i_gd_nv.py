# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import pandas as pd
from Tencant.engine import *



def str_time(zwtime):
    try:
        t = time.strptime(zwtime, '%Y年%m月%d日')
        r = time.strftime('%Y-%m-%d', t)
    except BaseException:
        return None
    else:
        pass
    return r


class TencentpositionSpider(scrapy.Spider):
    """
    光大保德信基金
    """
    # 爬虫名
    name = "gd_nv"
    allowed_domains = ['www.epf.com']

    def start_requests(self):
        start_urls = "http://www.epf.com.cn/index/search.js"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep - alive',
        }
        yield scrapy.Request(start_urls, callback=self.parse_id, headers=headers)

    def parse_id(self, response):
        a = response.text
        s = re.sub("\s|--", "", a)
        v = re.search("varfundmgArray=(.+?)<!\$检索数据end>", s).group(1)
        r = json.loads(v)
        ids = []
        for i in r:
            id = i['fundcode']
            ids.append(id)
        print(len(ids))
        for ID in ids:
            url_info = "http://www.epf.com.cn/fund/{}/basicinfo-zst.js".format(ID)
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            yield scrapy.Request(url_info, callback=self.parse_info, meta={"id": ID}, headers=headers, dont_filter=True)

    def parse_info(self, response):
        fund_id = response.meta['id']
        a = response.text
        s = re.sub("\s|--|\\\\", "", a)
        print(s)
        nv = re.search("varlinevalues={'data':(.+?)}<!\$基金概况-走势图end>", s).group(1)
        nv = nv.replace("'", '"')
        r = json.loads(nv)
        df = pd.DataFrame(r)
        df.columns = ["statistic_date", "nav", "added_nav"]
        df["fund_id"] = fund_id
        df["data_source"] = "000001"
        df["is_used"] = "1"
        df["is_del"] = "0"
        to_sql("i_fund_nv_gm", engine_data_test, df, type="update")





