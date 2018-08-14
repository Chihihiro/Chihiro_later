# -*- coding: utf-8 -*-
import scrapy
import http.cookiejar
import urllib.request, urllib.parse, urllib.error
from Tencant.engine import *



def reverse_baseN(string, b):
    _sign = "0123456789abcdefghijklmnopqrstuvwxyz"
    if len(string) == 1:
        return _sign.index(string)
    return _sign.index(string[-1]) + reverse_baseN(string[:-1], b) * b

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
        ll = response.xpath('/html/body/div[5]/div/div[1]/div[2]/table/tbody/tr/td[@class="t-company"]/a/@href').extract()
        for org_id in ll:
            org_url = "https://www.jfz.com{}".format(org_id)
            yield scrapy.Request(org_url, callback=self.parse_org, headers=self.headers, cookies=self.cookies)

    def parse_org(self, response):
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
        to_sql('__id_search_test', engine_data_test, df, type="update")




