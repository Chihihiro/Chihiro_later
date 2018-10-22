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
from Tencant.items import TencentItem, Tencentinfo, i_fund_info, d_org_info


def dff_df(df):
    df2 = df.T
    df4 = df2[df2[0] != ""]
    dff = df4.T
    return dff


dict = {
    TencentItem: "tencant",
    Tencentinfo: "tencant_info",
    i_fund_info: "d_fund_info",
    d_org_info: "d_org_info"
}

dict_engine = {
    TencentItem: engine5,
    Tencentinfo: engine5,
    i_fund_info: engine5,
    d_org_info: engine5
}


def clean(x):
    if type(x) is list:
        if x:
            y = [str(i) for i in x]
            return ','.join(y)
        else:

            return None
    else:
        return x

def for_columns(df):
    col = df.columns
    for i in col:
        df[i] = df[i].apply(lambda x: clean(x))
    return df

class TencentpositionSpider(object):
    def process_item(self, item, spider):
        c = pd.DataFrame([item])
        d = dff_df(c)
        df = for_columns(d)
        print(d)
        # print(type(item))
        to_sql(dict[type(item)], dict_engine[type(item)], df, type="update")
        return item

