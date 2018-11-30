# -*- coding: utf-8 -*-
import datetime
#当前时间（不是时间戳）
time_now = datetime.datetime.now()
#时分秒重置
#一天前
time_one_ago = (time_now - datetime.timedelta(days=1))
one_day_ago = time_one_ago.strftime("%Y-%m-%d")
print(one_day_ago)
#七天前
time_ago = (time_now-datetime.timedelta(days=7))
day_ago = time_ago.strftime("%Y-%m-%d")
print(day_ago)
#归因脚本配置参数;请参照神策数据提供的归因功能文稿
contribution_config = {
    'target_event': 'payOrderDetail',
    # 归因结果的计算属性,发在 sum 中为求和的属性，放在 unique 中为求 唯一值 的属性（如订单数）
    'target_property_sum': 'totalPriceOfProduct',
    'target_property_unique': 'orderID',
    # 下面属性作为结果结果次数的统计，记录订单详情中的唯一ID，如商品ID，为必须参数
    'target_join_property': 'productSKU',
    'touch_point_event': ['SviewProductDetailPage','SaddToShoppingcart'],
    'touch_point_join_property': 'productSKU',
    'mkt_event': 'mkt_event',
    'contribution_property': ['mkt_campaign', 'mkt_type','mkt_content'],
    # 归因时长的单位为天
    'mkt_time_length': 2,
    # 归因窗口期的选择，动态窗口和静态窗口只能选择一个, 选择动态窗口的话，则静态窗口无效
    # 动态时间设置，当需要让静态设置有效时， dynamic_time 设为 0 即可
    'dynamic_time': 7,
    'start_time': day_ago,
    'end_time': one_day_ago,
    # 归因结果文件的存放路径和命名
    'result_file': r'D:/fmysD/Sensors/funmart_contribution_result.xlsx',
    'sheet_name': 'mkt_contribution',
    # 归因类型，目前可选 last / first/ linear 三种
    'contribution_type': 'last'
}
# 此处配置神策分析的环境参数，以便能从环境中获取相应的数据，至少分析师权限的账号，且能读取全部数据
sensorsdata = {
    'url': 'http://47.91.104.157:8107',
    'project': 'production',
    'username': 'chenxiaoli@funmart.com',
    'password': '123123aA'
}

# 配置发送邮件的账户和密码
email_conf = {
    'address': '965958157@qq.com',
    'password': 'dsxvmnjiwgtrbecf',
    'server': 'smtp.qq.com'
}
# 归因邮件发送设置的内容，如主题、邮件体、收件人、抄送人
contri_email = {
    # 输入需要发送的邮件列表，用逗号区分
    'to_addrs': 'chenxiaoli@funmart.com',
    'cc_addrs': '',
    # 设置邮件体内容，支持 html
    'subject': '坑位归因结果报表',
    'body_content': '附件是此次归因的结果，请查收'
}

