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

class niko(scrapy.Item):
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
    source_id = scrapy.Field()
    foundation_date = scrapy.Field()
    fund_status = scrapy.Field()
    # purchase_status = scrapy.Field()
    # purchase_range = scrapy.Field()
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

class d_org_info(scrapy.Item):
    org_id = scrapy.Field()
    org_name = scrapy.Field()
    org_full_name = scrapy.Field()
    source_id = scrapy.Field()
    foundation_date = scrapy.Field()
    registered_capital = scrapy.Field()#注册资本
    management_scale = scrapy.Field()#管理规模
    manage_funds = scrapy.Field()#管理基金
    profit_fund = scrapy.Field()#盈利产品
    profit_share = scrapy.Field()#盈利产品比
    core_member = scrapy.Field()#核心成员
    # representative_products = scrapy.Field()#代表产品
    # representative_products_yield = scrapy.Field()#代表产品累计收益
    company_profile = scrapy.Field()#公司简介
    org_funds = scrapy.Field()#旗下基金
    org_team = scrapy.Field()#团队
    # whole_show = scrapy.Field()#核心人员
    # fund_custodian = scrapy.Field()
    # init_nav = scrapy.Field()
    # init_raise = scrapy.Field()
    # currency = scrapy.Field()
    # registration_holder = scrapy.Field()
    # region = scrapy.Field()
    pass