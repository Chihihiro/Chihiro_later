#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2018/12/28 0028 14:47 
# @Author : Chihiro 
# @Site :  
# @File : 下载图片.py 
# @Software: PyCharm

from urllib import request

img_url = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1545989806142&di=3f1e7349dfa950914ef440595080f620&imgtype=0&src=http%3A%2F%2Fpic1.win4000.com%2Fwallpaper%2F2018-11-26%2F5bfb63c57fe63.jpg"
# 保存图片到本地
request.urlretrieve(img_url, "壁纸.jpg")

