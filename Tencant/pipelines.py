# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class TencantPipeline(object):
#     def process_item(self, item, spider):
#         return item
from Tencant.engine import *
import pandas as pd
from Tencant.items import TencentItem, Tencentinfo, i_fund_info


def dff_df(df):
    df2 = df.T
    df4 = df2[df2[0] != ""]
    dff = df4.T
    return dff


dict = {
    TencentItem: "tencant",
    Tencentinfo: "tencant_info",
    i_fund_info: "i_fund_info_gm"
}

dict_engine = {
    TencentItem: engine5,
    Tencentinfo: engine5,
    i_fund_info: engine_data_test
}


class TencentpositionSpider(object):
    def process_item(self, item, spider):
        c = pd.DataFrame([item])
        d = dff_df(c)
        print(d)
        to_sql(dict[type(item)], engine_data_test, d, type="update")
        return item

