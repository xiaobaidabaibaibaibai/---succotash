# -*- coding: utf-8 -*-
import datetime
#当前时间的时间数组格式（仅年月日信息）
time_now = datetime.date.today()
#时分秒重置
#一天前
time_oneday_ago = (time_now - datetime.timedelta(days=1))
one_day_ago = time_oneday_ago.strftime("%Y-%m-%d %H:%M:%S")
one_day_ago_end = (time_now - datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
one_day_ago_date = time_oneday_ago.strftime("%Y-%m-%d")
print(one_day_ago)
#两天前
time_twoday_ago = (time_now-datetime.timedelta(days=2))
two_day_ago = time_twoday_ago.strftime("%Y-%m-%d %H:%M:%S")
two_day_ago_end = (time_oneday_ago-datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
two_day_ago_date = time_twoday_ago.strftime("%Y-%m-%d")
print(two_day_ago)
#七天前
time_week_ago = (time_now-datetime.timedelta(days=7))
day_week_ago = time_week_ago.strftime("%Y-%m-%d %H:%M:%S")
print(day_week_ago)

contribution_config = {
    #前一天的日期
    'start_time': one_day_ago_date ,
    #前一天的开始时间
    'start_time_begin': one_day_ago ,
    #前一天的结束时间
    'start_time_end': one_day_ago_end ,
    'end_time': two_day_ago_date ,
    'end_time_begin': two_day_ago ,
    'end_time_end': two_day_ago_end ,
    # 结果文件的存放路径和命名
    'result_file': None
}