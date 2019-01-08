#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2018/12/28 0028 10:24 
# @Author : Chihiro 
# @Site :  
# @File : riyu.py 
# @Software: PyCharm
print('riyu')
import scrapy
import re
import json
from scrapy.spiders import CrawlSpider
import time
from Tencant.items import niko


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
    单词抓取
    """
    # 爬虫名
    name = "nihongo"
    allowed_domains = ['jp.qsbdc.com']
    start_urls = "http://jp.qsbdc.com/jpword/index.php"

    def start_requests(self):
        start_urls = "http://jp.qsbdc.com/jpword/index.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep - alive',
        }
        yield scrapy.Request(start_urls, callback=self.parse, headers=headers)

    def parse(self, response):
        print(type(response))
        uu = response.xpath('/html/body/div[5]/div[2]/table/tbody/tr/td/a/text()')
        print(uu)
