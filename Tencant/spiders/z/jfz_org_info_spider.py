# -*- coding: utf-8 -*-
# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf-8')

"""
金斧子
"""

import scrapy
import re
import requests
from datetime import datetime
import time
from fund_spider.items import dOrgInfoItem, dOrgDpItem, dOrgFundItem, dOrgPersonItem
from util.str_clean import clean_str_strong
from bs4 import BeautifulSoup


class JFZorgspider(scrapy.Spider):
    name = "jfz_org_info_spider"
    allowed_domains = ['www.jfz.com']
    start_urls = ('https://www.jfz.com/simu/company.html',)
    version = datetime.today().strftime("%Y%m%d%H")
    custom_settings = {
        'COOKIES_ENABLED': True,  # 登陆后才显示净值数据
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'fund_spider.middlewares.RandomUserAgent.RandomUserAgent': 100,
            'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 110,
            # 'fund_spider.middlewares.RandomProxy.JFZProxy': 150,
            'fund_spider.middlewares.middleware.JFZLoginmiddleware': 160
        },
    }

    def login(self):
        session = requests.Session()
        url = 'https://passport.jinfuzi.com/passport/user/doLogin.html'
        session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

        # 金斧子账号  备用：18939862542 pwd： 68125542
        data = {"LoginForm[username]": "15026588463", "LoginForm[password]": "68125542"}
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
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=self.cookies, dont_filter=True, callback=self.parse_pages,
                                 meta={'retry': 0})

    def parse_pages(self, response):
        max_page_num = re.search('<li class="page-item page-last">\s*?<a href="(.*?)"></a></li>', response.body).group(
            1)
        max_page_num = int(re.search('\d+', max_page_num).group(0))
        # 返回的最大页面不准确
        max_page_num = 463
        self.log(max_page_num)
        for i in range(1, max_page_num + 1):
            url = 'https://www.jfz.com/simu/company_p%s.html' % i
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_org, meta={'retry': 0},
                                 dont_filter=True)

    def parse_org(self, response):
        self.log(response.url)
        records = re.findall('<td class="t-company">(.*?)咨询</a>', response.body, re.DOTALL)
        if not records and response.meta['retry'] < 2:
            print('%s未返回有效内容，重试第%d次，上限2次' % (response.url, response.meta['retry'] + 1))
            yield scrapy.Request(response.url, cookies=self.cookies, callback=self.parse_org,
                                 meta={'retry': response.meta['retry'] + 1},
                                 dont_filter=True)
        for record in records:
            org_name = clean_str_strong(re.search(' target="_blank">(.*?)</a>', record, re.DOTALL).group(1))
            org_id = re.search('<a href="/simu/c-(.*?).html" ', record, re.DOTALL).group(1)
            found_date = re.search('<td class="t-establish">(.*?)</td>', record, re.DOTALL).group(1)
            if found_date != '---':
                found_date = datetime.strptime(found_date, '%Y-%m-%d').date()
            area = re.search('<td class="t-area">(.*?)</td>', record, re.DOTALL).group(1)
            url = 'https://www.jfz.com/simu/c-%s.html' % org_id
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_info,
                                 meta={'org_name': org_name, 'org_id': org_id, 'retry': 0, 'found_date': found_date,
                                       'area': area}, dont_filter=True)
        # url = 'https://www.jfz.com/simu/c-CO000009C1.html'
        # yield scrapy.Request(url, cookies=self.cookies, callback=self.parse_info, dont_filter=True)

    def parse_info(self, response):
        self.log(response.url)
        soup = BeautifulSoup(response.body, 'lxml')
        item = dOrgInfoItem()
        item['org_name'] = response.meta['org_name'].strip()
        item['org_id'] = response.meta['org_id']
        item['found_date'] = response.meta['found_date']
        item['source_id'] = '020002'
        item['area'] = response.meta['area']
        item['org_full_name'] = response.xpath(
            '//div[@class="v4_simu_pro_info_states"]//li[@class="states_item states_item_large"]//span[@class="content"]/text()').extract()[
            0]
        item['core_member'] = response.xpath(
            '//div[@class="v4_simu_pro_info_states"]//li[@class="states_item"][3]//span[@class="content"]//text()').extract()[
            0]
        item['funds_num'] = response.xpath(
            '//div[@class="v4_simu_pro_info_states"]//li[@class="states_item"][2]//span[@class="content"]//text()').extract()[
            0]
        item['reg_capital'] = response.xpath(
            '//div[@class="v4_simu_pro_info_states"]//li[@class="states_item"][4]//span[@class="content"]//text()').extract()[
            0]
        item['found_date'] = response.meta['found_date']
        item['area'] = response.meta['area']
        item['version'] = self.version
        yield item
        trs = response.xpath(
            '//div[@class="v4_simu_pro_box fm_products"]//div[@class="v4_simu_pro_box_bd"]//div[@class="fm_tab_con active"]//tr')
        if trs:
            for tr in trs[1:]:
                item2 = dOrgFundItem()
                item2['org_name'] = response.meta['org_name'].strip()
                item2['org_id'] = response.meta['org_id']
                item2['source_id'] = '020002'
                item2['fund_name'] = clean_str_strong(tr.xpath('.//td[@class="tl"]//a/text()').extract()[0]).strip()
                item2['fund_id'] = '05' + re.search('/simu/p-(.+?).html',
                                                    tr.xpath('.//td[@class="tl"]//a/@href').extract()[0],
                                                    re.DOTALL).group(1)
                item2['version'] = self.version
                yield item2
        trs1 = response.xpath(
            '//div[@class="v4_simu_pro_box fm_products"]//div[@class="v4_simu_pro_box_bd"]//div[@class="fm_tab_con"]//tr')
        if trs1:
            for tr1 in trs1[1:]:
                item3 = dOrgFundItem()
                item3['org_name'] = response.meta['org_name'].strip()
                item3['org_id'] = response.meta['org_id']
                item3['source_id'] = '020002'
                item3['fund_name'] = clean_str_strong(tr1.xpath('.//td[@class="tl"]//a/text()').extract()[0]).strip()
                item3['fund_id'] = '05' + re.search('/simu/p-(.+?).html',
                                                    tr1.xpath('.//td[@class="tl"]//a/@href').extract()[0],
                                                    re.DOTALL).group(1)
                item3['version'] = self.version
                yield item3
        profile = soup.find('span', text=u'公司简介').find_next('div').text.strip()

        investment_idea = soup.find('span', text=u'投资理念')
        if investment_idea:
            investment_idea = investment_idea.find_next('div').text.strip()
        item4 = dOrgDpItem()
        item4['org_name'] = response.meta['org_name']
        item4['org_id'] = response.meta['org_id']
        item4['source_id'] = '020002'
        item4['profile'] = profile
        item4['investment_idea'] = investment_idea
        item4['version'] = self.version
        yield item4
        person_url = response.xpath(
            '//div[@class="v4_simu_pro_info_states"]//li[@class="states_item"][3]//span[@class="content"]//a/@href').extract()
        if person_url:
            person_id = re.search('/simu/m-(.+?).html', person_url[0], re.DOTALL).group(1)
            item5 = dOrgPersonItem()
            item5['org_name'] = response.meta['org_name'].strip()
            item5['org_id'] = response.meta['org_id']
            item5['source_id'] = '020002'
            item5['person_id'] = person_id
            item5['person_name'] = response.xpath(
                '//div[@class="v4_simu_pro_info_states"]//li[@class="states_item"][3]//span[@class="content"]//a/text()').extract()[
                0]
            item5['duty'] = '基金经理'
            item5['is_current'] = 1
            item5['version'] = self.version
            yield item5
