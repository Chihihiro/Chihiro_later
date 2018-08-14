# -*- coding: utf-8 -*-
import scrapy
from Tencant.items import TencentItem
import json


class TencentpositionSpider(scrapy.Spider):
    """
    功能：爬取腾讯社招信息
    """
    # 爬虫名
    name = "tencent"
    allowed_domains = ['hr.tencent.com']

    def start_requests(self):
        url = "http://hr.tencent.com/position.php?&start="
        for page in range(0, 3720, 10):
            start_urls = url + str(page)
            print(start_urls)
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            yield scrapy.Request(start_urls, callback=self.parse, meta={'page': page}, headers=headers)

    def parse(self, response):
        for each in response.xpath("//tr[@class='even'] | //tr[@class='odd']"):
            # 初始化模型对象
            item = TencentItem()
            # 职位名称
            item['positionname'] = each.xpath("./td[1]/a/text()").extract()[0]
            # 详情连接
            item['positionlink'] = each.xpath("./td[1]/a/@href").extract()[0]
            # 职位类别
            item['positionType'] = each.xpath("./td[2]/text()").extract()[0]
            # 招聘人数
            item['peopleNum'] = each.xpath("./td[3]/text()").extract()[0]
            # 工作地点
            item['workLocation'] = each.xpath("./td[4]/text()").extract()[0]
            # 发布时间
            item['publishTime'] = each.xpath("./td[5]/text()").extract()[0]
            yield item
