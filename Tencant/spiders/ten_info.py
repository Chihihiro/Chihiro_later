# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from Tencant.items import Tencentinfo
from sqlalchemy import create_engine

engine5 = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('root', '', 'localhost', 3306, 'test', ),
                        connect_args={"charset": "utf8"}, echo=True, )


class TencentpositionSpider(scrapy.Spider):
    """
    功能：爬取腾讯社招信息
    """
    # 爬虫名
    name = "tencent_info"
    allowed_domains = ['hr.tencent.com']

    def start_requests(self):
        url = "https://hr.tencent.com/"
        df = pd.read_sql("select positionlink from test.tencant", engine5)
        page = df["positionlink"].tolist()
        for id in page:
            start_urls = url + id
            print(start_urls)
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            yield scrapy.Request(start_urls, callback=self.parse, meta={'id': id}, headers=headers)

    def parse(self, response):
        id = response.meta['id']
        item = Tencentinfo()
        # 工作职责
        item['duty'] = response.xpath('//ul[@class="squareli"]').xpath("string(.)").extract()[0]
        item['work'] = response.xpath('//ul[@class="squareli"]').xpath("string(.)").extract()[1]
        item["id"] = id
        print(item)
        yield item
