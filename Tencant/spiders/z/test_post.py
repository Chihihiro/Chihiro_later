import requests


url = 'http://kong.citics.com/pub/api/v1/website/rzrq/rzrqObjects'
a = requests.post(url, data={'pageSize': 20, 'currPage': 2})
print(a.text)

r = requests.get(url,cookies = self.cookies,headers= self.headers)

# def test(self, response):
#     ll = response.xpath(
#         '/html/body/div[5]/div/div[1]/div[2]/table/tbody/tr/td[@class="t-company"]/a/@href').extract()
#     for org_id in ll:
#         org_url = "https://www.jfz.com{}".format(org_id)
#         # org_url = 'https://www.jfz.com/simu/c-CO00000A72.html'
#         url = 'https://www.jfz.com/public/login/Ajaxgetcompanydata'
#         formdata = {"Accept": "application/json, text/javascript, */*; q=0.01",
#                     "Host": "www.jfz.com",
#                     "Origin": "https: // www.jfz.com",
#                     "Referer": org_url,
#                     "X-Requested-With": "XMLHttpRequest",
#                     "Cookie": "Hm_lvt_9cfdc8c0bb3c0ab683956289eef9f34a=1539911047; JRECORD_UID=7e38bdf53711ce84a1083799514d044f; JRECORD_FTIME=1539911047; gr_user_id=057c2f88-52d3-471f-bcec-e3ca10df5513; _smt_uid=5bc92d88.b61ad11; compare_index=0%26%261%26%262%26%263; MEIQIA_EXTRA_TRACK_ID=1BS7fDEEKPKISFAUqTzQN77ZgFk; JRECORD_LANDPAGE=https%3A%2F%2Fwww.jfz.com%2Fsimu%2Fc-CO00000A73.html; PHPSESSID=mtti6moeb52odn9vc8sfv8t6h0; jfzWebUser=e5c42481e721a39deb82cf1369ba06df4e372c2da%3A4%3A%7Bi%3A0%3Bs%3A10%3A%226176844059%22%3Bi%3A1%3Bs%3A11%3A%2215026588463%22%3Bi%3A2%3Bi%3A86400%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D; jfz_login_id=6176844059; accessToken=ebf9253d2cf9d60c06efd2e46357b80c; jfz_user_type=0; MEIQIA_VISIT_ID=1BmQEVvxyHVuuRRJ0vQfLzNbgSc; JRECORD_LTIME=1539925714; gr_session_id_9907c51ef09823c8d5b98c511e30a866=c75611c7-0ca8-40b2-a614-2b7ae290f378; gr_cs1_c75611c7-0ca8-40b2-a614-2b7ae290f378=user_id%3A6176844059; gr_session_id_9907c51ef09823c8d5b98c511e30a866_c75611c7-0ca8-40b2-a614-2b7ae290f378=true; JRECORD_CTIME=1539929257; Hm_lpvt_9cfdc8c0bb3c0ab683956289eef9f34a=1539929257",
#                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
#         scrapy.FormRequest(url, callback=self.parse_org, method='POST', formdata=formdata)

import requests
import json

url = "http://example.com"
data = {
    'a': 1,
    'b': 2,
}
#1
requests.post(url, data=json.dumps(data))
# 2-json参数会自动将字典类型的对象转换为json格式
requests.post(url, json=data)
