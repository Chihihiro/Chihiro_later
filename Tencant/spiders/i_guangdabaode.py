# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
from Tencant.items import i_fund_info


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
    name = "guangdabaode"
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
        for ID in ids:
            url_info = "http://www.epf.com.cn/fund/{}/info.shtml".format(ID)
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            yield scrapy.Request(url_info, callback=self.parse_info, meta={"id": ID}, headers=headers, dont_filter=True)

    def parse_info(self, response):
        fund_id = response.meta['id']
        item = i_fund_info()
        # print(response.text)
        # ids = response.xpath('//ul[@class="squareli"]').xpath("string(.)").extract()
        item['fund_full_name'] = response.xpath('//*[@id="main"]/div[3]/table/tr[1]/td/text()').extract()[0]
        item['fund_name'] = response.xpath('//*[@id="main"]/div[3]/table/tr[2]/td/text()').extract()[0]
        item['fund_id'] = fund_id
        item["fund_type"] = response.xpath('//*[@id="main"]/div[3]/table/tr[4]/td/text()').extract()[0]
        item['fund_manager'] = response.xpath('//*[@id="main"]/div[3]/table/tr[7]/td/text()').extract()[0]
        item['foundation_date'] = re.sub("\s", "", response.xpath('//*[@id="main"]/div[3]/table/tr[6]/td/text()').extract()[0])
        item['recommendation_start'] = response.xpath('//*[@id="main"]/div[3]/table/tr[5]/td/text()').extract()[0]
        item['recommendation_end'] = response.xpath('//*[@id="main"]/div[3]/table/tr[5]/td/text()').extract()[0]
        item['fund_manager_nominal'] = response.xpath('//*[@id="main"]/div[3]/table/tr[14]/td/text()').extract()[0]
        item['fund_custodian'] = response.xpath('//*[@id="main"]/div[3]/table/tr[15]/td/text()').extract()[0]
        item['data_source'] = '000001'
        item["foundation_date"] = str_time(item["foundation_date"])
        try:
            if "至" in item["recommendation_start"]:
                item["recommendation_start"] = str_time(item["recommendation_start"].split("至")[0])
                item["recommendation_end"] = str_time(item["recommendation_end"].split("至")[1])
            else:
                item["recommendation_start"] = str_time(item["recommendation_start"])
                item["recommendation_end"] = None
        except BaseException:
            pass
        else:
            pass
        print(item)

        yield item





