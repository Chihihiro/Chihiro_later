# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Tencentinfo(scrapy.Item):
    duty = scrapy.Field()
    work = scrapy.Field()
    id = scrapy.Field()
    pass


class TencentItem(scrapy.Item):

    # 职位名
    positionname = scrapy.Field()
    # 详情连接
    positionlink = scrapy.Field()
    # 职位类别
    positionType = scrapy.Field()
    # 招聘人数
    peopleNum = scrapy.Field()
    # 工作地点
    workLocation = scrapy.Field()
    # 发布时间
    publishTime = scrapy.Field()
    pass



class i_fund_info(scrapy.Item):
    fund_id = scrapy.Field()
    fund_name = scrapy.Field()
    fund_full_name = scrapy.Field()
    data_source = scrapy.Field()
    foundation_date = scrapy.Field()
    fund_status = scrapy.Field()
    purchase_status = scrapy.Field()
    purchase_range = scrapy.Field()
    redemption_status = scrapy.Field()
    aip_status = scrapy.Field()
    fund_trustee = scrapy.Field()
    recommendation_start = scrapy.Field()
    recommendation_end = scrapy.Field()
    operation_mode = scrapy.Field()
    fund_type = scrapy.Field()
    fund_manager = scrapy.Field()
    fund_manager_nominal = scrapy.Field()
    fund_custodian = scrapy.Field()
    init_nav = scrapy.Field()
    init_raise = scrapy.Field()
    currency = scrapy.Field()
    registration_holder = scrapy.Field()
    region = scrapy.Field()
    pass


class JFZ(scrapy.Item):
    duty = scrapy.Field()
    work = scrapy.Field()
    id = scrapy.Field()
    pass

