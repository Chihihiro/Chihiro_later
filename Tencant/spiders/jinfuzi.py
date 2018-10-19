# -*- coding: utf-8 -*-
import scrapy
import http.cookiejar
import urllib.request, urllib.parse, urllib.error
from Tencant.engine import *
from Tencant.items import d_org_info

def reverse_baseN(string, b):
    _sign = "0123456789abcdefghijklmnopqrstuvwxyz"
    if len(string) == 1:
        return _sign.index(string)
    return _sign.index(string[-1]) + reverse_baseN(string[:-1], b) * b

def str_time(zwtime):
    try:
        t = time.strptime(zwtime, '%Y年%m月%d日')
        r = time.strftime('%Y-%m-%d', t)
    except BaseException:
        return None
    else:
        pass
    return r


def login():
    login_url = 'https://passport.jinfuzi.com/passport/user/doLogin.html'
    values = {'paramMap.password': '68125542', 'paramMap.userName': '15026588463'}
    postdata = urllib.parse.urlencode(values).encode()
    user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    headers = {'User-Agent': user_agent}
    cookie_filename = 'cookie_jar.txt'
    cookie_jar = http.cookiejar.MozillaCookieJar(cookie_filename)
    handler = urllib.request.HTTPCookieProcessor(cookie_jar)
    opener = urllib.request.build_opener(handler)
    try:
        print('-------------')
        request = urllib.request.Request(login_url, data=postdata, headers=headers, method='POST')
        response = opener.open(request)
    except urllib.error.URLError as e:
        print(e.code, ':', e.reason)
    cookie_jar.save(ignore_discard=True, ignore_expires=True)  # 保存cookie到cookie.txt中

    for item in cookie_jar:
        print('Name = ' + item.name)
        print('Value = ' + item.value)

        cook = item.value
        cookise = {'Cookie': cook}
        return cookise


class TencentpositionSpider(scrapy.Spider):
    name = "jinfuzi"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    cookies = login()

    def start_requests(self):
        for page in range(1, 500, 1):
            if page == 1:
                start_url = "https://www.jfz.com/simu/company.html"
            else:
                pp = "_p" + str(page)
                start_url = "https://www.jfz.com/simu/company{}.html".format(pp)
            yield scrapy.Request(start_url, callback=self.parse_page, headers=self.headers, cookies=self.cookies)

    def parse_page(self, response):
        ll = response.xpath(
            '/html/body/div[5]/div/div[1]/div[2]/table/tbody/tr/td[@class="t-company"]/a/@href').extract()
        for org_id in ll:
            org_url = "https://www.jfz.com{}".format(org_id)
            yield scrapy.Request(org_url, callback=self.parse_org, meta={"org_id": org_id}, headers=self.headers, cookies=self.cookies)






    def parse_org(self, response):
        print(response)

        ll = response.xpath('//*[@id="yxz"]/div[2]/table/tbody/tr/td[@width="190"]/a/@href').extract()
        ids = []
        for i in ll:
            id = re.search('/simu/p-(.+?).html', i).group(1)
            ids.append(id)

        c = {
            "fund_id": ids
        }

        data = pd.DataFrame(c)
        data["source_id"] = '020002'
        data["P"] = data["fund_id"].apply(lambda x: x[1:] if x[0] == "P" else None)
        data["id_time"] = data["P"].apply(lambda x: str(int(reverse_baseN(x, 36))) if type(x) is str else x)
        df = data.drop(["P"], axis=1)
        print(data)
        to_sql('__id_search', engine5, df, type="update")

        item = d_org_info()
        org_id = response.meta['org_id']
        item['org_id'] = org_id
        item['org_full_name'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[1]/span[2]/@title').extract()
        item['foundation_date'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[2]/span[2]/text()').extract()
        item['registered_capital'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[5]/span[2]/text()').extract()
        item['management_scale'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[8]/span[2]/text()').extract()
        item['manage_funds'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[3]/span[2]/text()').extract()
        item['profit_fund'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[6]/span[2]/text()').extract()
        item['profit_share'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[9]/span[2]/span/text()').extract()
        item['core_member'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[4]/span[2]/text()').extract()
        item['representative_products'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[7]/span[2]/a/text()').extract()
        item['representative_products_yield'] = response.xpath('/html/body/div[6]/div/div[1]/div[2]/ul/li[10]/span[2]/text()').extract()

        # item['company_profile'] = response.xpath().extract()
        item['org_funds'] = ','.join(response.xpath('//*[@id="box1"]/table/tbody/tr'
                                            '/td/a/@title').extract())+','+','.join(
            response.xpath('//*[@id="yqs"]/div[2]/table/tbody/tr[1]/td[1]/a/@title').extract()
        )
        try:
            item["foundation_date"] = str_time(item["foundation_date"][0])
        except BaseException:
            item["foundation_date"] = None
        else:
            pass

        print(item["foundation_date"])

        yield item


