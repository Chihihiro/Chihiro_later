import pandas as pd
import sys

from sqlalchemy import create_engine
import numpy as np
from Tencant.iosjk import *

engine_crawl = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
    'root', 'chihiro123', '47.107.35.189', 3306, 'crawl', ), connect_args={"charset": "utf8"}, echo=True, )

engine5 = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('root', 'chihiro123', 'localhost', 3306, 'crawl', ),
                        connect_args={"charset": "utf8"}, echo=True, )


# engine_basetest = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('root','','localhost',3306,'base.test', ), connect_args={"charset": "utf8"},echo=True,)
# engine_base = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('jr_admin_qxd', 'jr_admin_qxd', '182.254.128.241', 4171, 'base', ),connect_args={"charset": "utf8"}, echo=True, )
# engine_crawl_private = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('jr_admin_qxd', 'jr_admin_qxd', '182.254.128.241', 4171, 'crawl_private', ),connect_args={"charset": "utf8"}, echo=True, )
# engine_crawl = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('jr_admin_qxd', 'jr_admin_qxd', '182.254.128.241', 4171, 'crawl', ),connect_args={"charset": "utf8"}, echo=True, )
# engine_base_public = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('jr_admin_qxd', 'jr_admin_qxd', '182.254.128.241', 4171, 'base_public', ),connect_args={"charset": "utf8"}, echo=True, )


def to_table(df):
    df.to_csv("C:\\Users\\63220\\Desktop\\Pycharm测试{}.csv".format(now2))


def to_table_excel(df):
    writer = pd.ExcelWriter("C:\\Users\\63220\\Desktop\\Pycharm{}.xlsx".format(now2))
    df.to_excel(writer, "Sheet1")
    writer.save()


def to_zd(df):
    a = np.array(df)  # np.ndarray()
    vv = set(a)  # list
    return vv


def to_list(df):
    a = np.array(df)  # np.ndarray()
    vv = a.tolist()  # list
    return vv


import time

now = time.strftime("%Y-%m-%d")
now2 = time.strftime("%Y%m%d%H%M")


def now_time(a=0):
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=a)
    n_days = now + delta
    print(n_days.strftime('%Y-%m-%d %H:%M:%S'))
    f = n_days.strftime('%Y-%m-%d')
    return f


import datetime


def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates


# def info_to_table():
#     df = pd.read_sql(
#         "Select fund_id,reg_code,fund_name,fund_full_name,foundation_date,fund_manager,fund_manager_nominal,fund_id from base.fund_info ORDER BY fund_id DESC ;",
#         engine_base)
#     to_table_excel(df)
#     print(now2)
#     print('已经保存桌面')


dict_table = {"010002": "x_fund_info_fundaccount",
              "010003": "x_fund_info_private",
              "010004": "x_fund_info_securities",
              "010005": "x_fund_info_futures",
              "020001": "d_fund_info",
              "020002": "d_fund_info",
              "020003": "d_fund_info",
              }


# def fund_full_name(fund_id):
#     df = pd.read_sql("select source_id,source from id_match WHERE matched_id='{}' \
#     and is_used=1 AND source not in ('010001','000001','020004','020005','020007') and source not like '03%%' and source not like'04%%' and source not like'05%%'".format(
#         fund_id), engine_base)
#     num = len(df)
#
#     df['fund_tabel'] = df['source'].apply(lambda x: dict_table.get(x))
#     df["fund_full_name"] = None
#     for i in range(num):
#         a = df.iloc[i, 0]
#         b = df.iloc[i, 1]
#         c = df.iloc[i, 2]
#         if b in ('020001', '020002', '020003'):
#             name = pd.read_sql(
#                 "SELECT DISTINCT fund_name FROM d_fund_info WHERE fund_id='{}' and source_id='{}' and  version>10".format(
#                     a, b),
#                 engine_crawl_private)
#             try:
#                 full_name = name.iloc[0, 0]
#                 df.iloc[i, 3] = full_name
#             except BaseException:
#                 full_name = '空'
#                 df.iloc[i, 3] = full_name
#             else:
#                 pass
#         else:
#             name = pd.read_sql("SELECT DISTINCT fund_name_amac FROM {} where fund_id='{}'".format(c, a),
#                                engine_crawl_private)
#             full_name = name.iloc[0, 0]
#             df.iloc[i, 3] = full_name
#     print(df)
#     L = df["fund_full_name"]
#     list = to_list(L)
#     return list
