# -*- coding: utf-8 -*-
# 2018-08-01
# 此文件主要存放一些可能在多个脚本中都使用的函数
import json
from config import sensorsdata, contribution_config
import requests
from datetime import date, timedelta, datetime
from time import time
import math
import pandas as pd


def handle_contribution_config(conf):
    if conf['dynamic_time']:
        conf['start_time'] = date.today() - timedelta(days=conf['dynamic_time']+1)
        conf['end_time'] = date.today() - timedelta(days=1)
        conf['mkt_start_time'] = date.today() - timedelta(days=conf['dynamic_time']+1+conf['mkt_time_length'])
        conf['target_join_property'] = conf['target_join_property'].lower()
        conf['contribution_property'] = [i.lower() for i in conf['contribution_property']]
        conf['target_property_sum'] = conf['target_property_sum'].lower()
    else:
        conf['mkt_start_time'] = (pd.to_datetime(conf['start_time']) - timedelta(days=1)).strftime('%Y-%m-%d')
        conf['target_join_property'] = conf['target_join_property'].lower()
        conf['contribution_property'] = [i.lower() for i in conf['contribution_property']]
        conf['target_property_sum'] = conf['target_property_sum'].lower()
    return conf

def delete_url_slash(url):
    """
    :param url: 用户配置或输入的 url
    :return: 去除最后斜线后的 url
    """
    if url[0] == '/':
        return url[:-1]
    else:
        return url


def obtain_token():
    """
    此方法使用配置文件中 sensorsdata 的参数
    此方法用于获取 Login 接口中返回的 Cookie，
    :return: cookie 中的 token
    """
    url = delete_url_slash(sensorsdata.get('url')) + '/api/auth/login'
    params = {
        'project': sensorsdata.get('project')
    }
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'Paw/3.1 (Macintosh; OS X/10.12.6) GCDHTTPRequest'
    }
    data = {
        'username': sensorsdata.get('username'),
        'password': sensorsdata.get('password')
    }
    response = requests.post(url=url, params=params, headers=headers, data=json.dumps(data))
    if response.json()['token']:
        print("get the token successfully")
    return response.json()['token']
    

class Map(dict):
    """
    该对象为了模拟可以使用 . 直接获取 Json 中的变量，主要用于配置文件
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    if isinstance(v, list):
                        self.__convert(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = Map(v)
                elif isinstance(v, list):
                    self.__convert(v)
                self[k] = v

    def __convert(self, v):
        for elem in range(0, len(v)):
            if isinstance(v[elem], dict):
                v[elem] = Map(v[elem])
            elif isinstance(v[elem], list):
                self.__convert(v[elem])

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


# arr:需要循环加字母的数组
# level：需要加的层级
def cycle_letter(arr, level):
    tmp_arr = []
    letter_arr = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', \
                  'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    arr_num = len(arr)
    if level == 0 or arr_num == 0:
        return letter_arr
    for index in range(arr_num):
        for letter in letter_arr:
            tmp_arr.append(arr[index] + letter)
    return tmp_arr


# arr:需要生成的Excel列名称数目
def reduce_excel_col_name(num):
    tmp_var = 1
    level = 1
    while tmp_var:
        tmp_var = num / (math.pow(26, level))
        if tmp_var > 1:
            level += 1
        else:
            break
    
    excel_arr = []
    temp_arr = []
    for index in range(level):
        temp_arr = cycle_letter(temp_arr, index)
        for numIndex in range(len(temp_arr)):
            if len(excel_arr) < num:
                excel_arr.append(temp_arr[numIndex])
            else:
                return excel_arr


class ScriptsTimer():
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = datetime.now()
        self.start_count = time()
        print("-" * 10 + "Script start" + "-" * 10)
    
    def time_counter(self, content="Already time cost:"):
        self.time_count = time()
        print("-" * 5 + content + "%ss" % int(self.time_count - self.start_count) + "-" * 5)
    
    def end(self):
        self.end_time = datetime.now()
        self.end_count = time()
        print("-" * 5 + "Script stop, total time: %ss" % int(self.end_count - self.start_count) + "-" * 5)


if __name__ == '__main__':
    print(handle_contribution_config(contribution_config))
