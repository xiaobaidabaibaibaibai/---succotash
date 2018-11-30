# -*- coding: utf-8 -*-

import json
import pandas as pd
import requests
from config import one_day_ago_date,two_day_ago_date,contribution_config
from baidu_api import baidu_translate

def obtain_data_from_url():
    """
    神策HQL取数
    :return: sql查询结果
    """
    sql = '''
select 
        b.q,b.times,a.ranking_yesterday,b.ranking_today,a.ranking_yesterday-b.ranking_today
    from
        (select 
            date,q,COUNT(returnResult) times,row_number() OVER (PARTITION BY date ORDER BY count(returnresult) desc) ranking_yesterday
        from events 
        where date = '{two_day_ago_date}'and
            time between '{two_day_ago}' and '{two_day_ago_end}' and 
            event='SsearchResult'
            group by date,q ) as a 
        left join 
        (select 
            date,q,COUNT(returnResult) times,row_number() OVER (PARTITION BY date ORDER BY count(returnresult) desc) ranking_today
        from events 
        where date = '{one_day_ago_date}' and
            time between '{one_day_ago}' and '{one_day_ago_end}' and 
            event='SsearchResult'
        group by date,q ) as b 
    on a.q=b.q 
    where b.q is not null 
    group by b.q,b.times,a.ranking_yesterday,b.ranking_today
    '''.format(two_day_ago_date = contribution_config['end_time'], two_day_ago = contribution_config['end_time_begin'],
               two_day_ago_end = contribution_config['end_time_end'], one_day_ago_date =contribution_config['start_time'],
               one_day_ago = contribution_config['start_time_begin'], one_day_ago_end = contribution_config['start_time_end'] )

    url = "http://47.91.104.157:8107/api/sql/query?token=73b7fce4eb8761674fefc642edac278d514a7a5092d391d079c65ed829a015cf&project=production&format=cav&q="
    start_url = url + sql
    response = requests.get(start_url)
    df = pd.read_json(response.text, lines=True)
    print(df)
    print("get the data from sa successfully, {} lines and {} columns.".format(df.shape[0], df.shape[1]))
    return df

def storage_excel_saved(df, path):
    """
    保存为excel
    :param path:文件存放路径
    :param df:sql查询结果
    :return:文件名
    """
    filename = one_day_ago_date + '和' + two_day_ago_date + '两天查询内容排名比较'
    path_rt = path + filename + '.csv'
    print(path_rt)
    #writer = pd.ExcelWriter(path=path_rt, engine='xlsxwriter')
    df1=df['q']
    print(df1)
    list=[]
    for i in df1:
        list.append(i)
     print(list)
    df2=baidu_translate(df1)
    print(df2)
    df.to_csv(path_rt, sep=',',encoding='utf-8-sig')
    print("已输出"+filename)
    return path_rt

def DingDingPMSRobot_MSG_send(message_url, usr_msg, atMen):
    """
    钉钉推送接口
    :param message_url: 发送的消息内容，url，文字或者markdown
    :param usr_msg: 用户自定义消息
    :param atMen: @某个人，逗号分隔
    :param atAll: @所有人，默认为0，有需要改1
    :return: None
    """
    token = '057f7bdf2d02cbe8a6da3960c9761673b5301dc994702fc25ef3e0260cd781d6'
    ddUrl_msg = 'https://oapi.dingtalk.com/robot/send?access_token='
    url = ddUrl_msg + token
    msg = message_url + usr_msg
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/json"
    }
    String_textMsg = {
        "msgtype": "text",
        "text": {"content": msg},
        "at": {
            "atMobiles": [
                atMen  # 这里填写需要@的用户的手机号码，字符串或数字都可以
            ]
            , "isAtAll": "false"
        }
    }
    String_textMsg = json.dumps(String_textMsg).encode(encoding='utf-8')
    res = requests.post(url, data=String_textMsg, headers=HEADERS)
    print(res.content)

if __name__ == '__main__':
    sql_result = obtain_data_from_url()
    file_path = storage_excel_saved(sql_result, 'D://BaiduNetdiskDownload/2.xlsx')
    # DingDingPMSRobot_MSG_send(file_path, '', '袁淼')
