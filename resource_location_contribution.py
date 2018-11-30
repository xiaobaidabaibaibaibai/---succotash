# -*- coding: utf-8 -*-
# 2018-07-30
# 此脚本主要计算产品内部不同坑位、不同活动对目标行为的影响。使用者可通过本脚本获取明细数据，或自行修改实现更灵活的功能

from config import contribution_config, sensorsdata
from public_function import obtain_token, delete_url_slash, handle_contribution_config, reduce_excel_col_name, ScriptsTimer
import pandas as pd
import requests


def obtain_data_from_sa(token):
    """
    函数参数都在配置文件中，若无法执行，请完善配置文件
    :return: 返回用于归因的初步数据
    """
    print("Begin to request data from SA")
    url = delete_url_slash(sensorsdata.get('url')) + '/api/sql/query'
    # 获取归因的 raw_data
    exe_sql = '''
      select mkt_e.user_id, mkt_e.time mkt_time, mkt_e.event mkt_event, {contribution_property},
      touch_point_time, touch_point_event, target_time, target_event, touch_point.{target_property}, touch_point.{target_join_property}
    from  events mkt_e
    join (select e.user_id, e.time touch_point_time, e.event touch_point_event, target.time target_time,
        target.event target_event, target.{target_join_property}, target.{target_property}
        from events e
        join (select user_id, time, event, {target_join_property}, {target_property}
            from events
            where event = '{target_event}'  and date between '{start_time}' and '{end_time}') target
            on e.user_id = target.user_id and e.time between target.time - interval '{mkt_time_length}' day and target.time and e.{touch_point_join_property} = target.{target_join_property}
        where e.event in ({touch_point_event}) and e.date between '{mkt_start_time}' and '{end_time}') touch_point
        on mkt_e.user_id = touch_point.user_id and mkt_e.time between touch_point.touch_point_time  - interval '{mkt_time_length}' day and touch_point.touch_point_time
    where mkt_e.event = '{mkt_event}'
    '''.format(target_event=contribution_config['target_event'], start_time=contribution_config['start_time'],
               end_time=contribution_config['end_time'],
               target_join_property=contribution_config['target_join_property'],
               mkt_start_time=contribution_config['mkt_start_time'],
               target_property=contribution_config['target_property_sum'],
               mkt_time_length=contribution_config['mkt_time_length'],
               touch_point_event=str(contribution_config['touch_point_event'])[1:-1],
               touch_point_join_property=contribution_config['touch_point_join_property'],
               mkt_event=contribution_config['mkt_event'],
               contribution_property=','.join(['mkt_e.' + x for x in contribution_config['contribution_property']]))
    response = requests.post(url=url, data={'project': sensorsdata.get('project'),
                                            'q': exe_sql, 'format': 'json'},
                             headers={'sensorsdata-token': token})
    df = pd.read_json(response.text, lines=True)
    print("get the data from sa successfully, {} lines and {} columns.".format(df.shape[0], df.shape[1]))
    return df


def tidy_data(df_raw, target_element_id):
    """
    进行数据处理，生成实现多种归因方案的基础数据
    :param df_raw:
    :return:
    """
    print('Start to tidy data...')
    
    # 去除多余的 营销事件，获取每一个触点最近的一个营销事件
    df_tmp = df_raw.sort_values('mkt_time', ascending=False).drop_duplicates(
        ['user_id', 'touch_point_event', 'touch_point_time', 'target_event', 'target_time', target_element_id])
    
    # 有可能一个触点最近的一个营销事件，是超过了上一个触点的时间的，所以需要排除此类情况
    # 先按照触点的时间进行排序，准备进行比较，去除营销时间超过上一个触点时间的情况
    df_tmp.sort_values(by=['user_id', 'target_event', target_element_id, 'target_time', 'touch_point_time'],
                       inplace=True)  # 排序替换
    df_tmp_1 = df_tmp[~((df_tmp.mkt_time < df_tmp.touch_point_time.shift()) & (df_tmp.user_id == df_tmp.user_id.shift()) \
                        & (df_tmp.target_event == df_tmp.target_event.shift()) & (
                            df_tmp.target_time == df_tmp.target_time.shift()) \
                        & (df_tmp[target_element_id] == df_tmp[target_element_id].shift()))]
    
    # 增加一列转化的总营销事件数
    df_tmp_2 = df_tmp_1.groupby(['target_event', 'target_time', 'user_id', target_element_id]).size().to_frame(
        'factor_num')
    df_final = df_tmp_1.join(df_tmp_2, how='left', on=['target_event', 'target_time', 'user_id', target_element_id])
    
    # 增加营销因子的排序信息
    df_final.sort_values(by=['user_id', 'target_event', target_element_id, 'target_time', 'mkt_time'], inplace=True)
    df_final['factor_rank'] = df_final.groupby(['user_id', 'target_event', target_element_id, 'target_time', ])[
        'mkt_time'].rank(method='dense').astype('int')
    print('Tidy data process completed.')
    return df_final


def obtain_click_summary_data_from_sa(token):
    """
    从神策获取坑位在某段时间内的点击次数和人数，从而计算总体的次数转化率和人数转化率
    :return:
    """
    print("Begin to request click summary data from SA")
    url = delete_url_slash(sensorsdata.get('url')) + '/api/sql/query'
    exe_sql = '''
    select  {contribution_property}, count(distinct user_id) mkt_users, sum(click_qty) mkt_times
    from (select user_id, {contribution_property}, count(1) click_qty
    from events e
    where event = '{mkt_event}' and date between  '{mkt_start_time}' and '{end_time}'
    group by user_id, {contribution_property}) mkt_e
    group by {contribution_property}
    '''.format(contribution_property=','.join(contribution_config['contribution_property']),
               mkt_event=contribution_config['mkt_event'],
               mkt_start_time=contribution_config['mkt_start_time'],
               end_time=contribution_config['end_time'])
    response = requests.post(url=url, data={'project': sensorsdata.get('project'),
                                            'q': exe_sql, 'format': 'json'},
                             headers={'sensorsdata-token': token})
    df = pd.read_json(response.text, lines=True)
    print("get the data from sa successfully, {} lines and {} columns.".format(df.shape[0], df.shape[1]))
    return df


def calculate_contribution(df_raw, df_summary, conf):
    """
    计算多种不同归因方式的结果
    :param df_raw: 数据清洗过后，用于归因的原始数据，由 tidy_data 生成
    :param df_summary: 用户计算归因的次数转化和人数转化，由 obtain_click_summary_data_from_sa 生成
    :param contribution_type: 归因类型，目前支持 last/ first/ linear
    :param conf: 被处理过后的配置文件
    :return: 返回最终归因的结果数据
    """
    # 末次归因方式逻辑
    if conf['contribution_type'] == 'last':
        df_c = df_raw.query("factor_num == factor_rank")
        df_r = df_c.groupby(conf['contribution_property'], as_index=False).agg(
            {conf['target_property_sum']: ['sum'],
             'user_id': pd.Series.nunique, conf['target_join_property']: pd.Series.nunique})
        # 处理 multi index
        df_r.columns = list(map(''.join, df_r.columns.values))
        df_contribution = pd.merge(df_r, df_summary, on=conf['contribution_property'], how='left')
        # 计算营销事件的次数转化率和人数转化率
        df_contribution['mkt_click_conversion_rate'] = df_contribution[conf['target_join_property'] + 'nunique'] \
                                                       / df_contribution['mkt_times']
        df_contribution['mkt_user_conversion_rate'] = df_contribution['user_id'+'nunique'] \
                                                       / df_contribution['mkt_times']
        return df_contribution
    
    if conf['contribution_type'] == 'first':
        df_c = df_raw.query("factor_rank == 1")
        df_r = df_c.groupby(conf['contribution_property'], as_index=False).agg(
            {conf['target_property_sum']: ['sum'],
             'user_id': pd.Series.nunique, conf['target_join_property']: pd.Series.nunique})
        # 处理 multi index
        df_r.columns = list(map(''.join, df_r.columns.values))
        df_contribution = pd.merge(df_r, df_summary, on=conf['contribution_property'], how='left')
        # 计算营销事件的次数转化率和人数转化率
        df_contribution['mkt_click_conversion_rate'] = df_contribution[conf['target_join_property'] + 'nunique'] \
                                                       / df_contribution['mkt_times']
        df_contribution['mkt_user_conversion_rate'] = df_contribution['user_id' + 'nunique'] \
                                                      / df_contribution['mkt_times']
        return df_contribution
    
    if conf['contribution_type'] == 'linear':
        # 线性归因遇到人数、商品数这种数据时，无法对人数既进行去重，又进行分数相乘
        df_c = df_raw
        df_r = df_c.groupby(conf['contribution_property'], as_index=False).agg(
            {conf['target_property_sum']: lambda x: sum(x/df_c.loc[x.index].factor_num),
             'user_id': pd.Series.nunique, conf['target_join_property']: pd.Series.nunique})
        # 处理 multi index
        df_r.columns = list(map(''.join, df_r.columns.values))
        df_contribution = pd.merge(df_r, df_summary, on=conf['contribution_property'], how='left')
        # 线性的模式，之后的 header 不会加 sum/unique 后缀，需要加上
        df_contribution.rename(inplace=True, columns={conf['target_property_sum']: conf['target_property_sum'] + 'sum',
                                                      conf['target_join_property']: conf['target_join_property'] + 'nunique',
                                                      'user_id': 'user_id' + 'nunique'})
        # 计算营销事件的次数转化率和人数转化率
        df_contribution['mkt_click_conversion_rate'] = df_contribution[conf['target_join_property'] + 'nunique'] \
                                                       / df_contribution['mkt_times']
        df_contribution['mkt_user_conversion_rate'] = df_contribution['user_id' + 'nunique'] \
                                                      / df_contribution['mkt_times']
        return df_contribution
        

def add_condition_format(path, df, conf):
    writer = pd.ExcelWriter(path=path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=conf['sheet_name'])
    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets[conf['sheet_name']]
    # 获取哪些列需要颜色标识
    contribution_num = len(conf['contribution_property'])
    column_list = reduce_excel_col_name(df.columns.size + 1)
    # 增加行列的宽度
    worksheet.set_column('{}:{}'.format(column_list[0], column_list[-1]), width=16)
    worksheet.set_default_row(16)
    # 修改最后两列为百分比格式
    format_percent = workbook.add_format({'num_format': '0.00%'})
    for column in column_list[-2:]:
        worksheet.set_column('{col}:{col}'.format(col=column), 16, format_percent)
    
    # Apply a conditional format to the cell range.
    # 给数值列添加颜色
    for column in column_list[contribution_num + 1:]:
        worksheet.conditional_format('{column}2:{column}{lines}'.format(column=column, lines=df.index.size),
                                     {'type': '2_color_scale',
                                      'min_color': '#FFFFFF',
                                      'max_color': '#00B885'})
    writer.save()


if __name__ == '__main__':
    timer = ScriptsTimer()
    timer.start()
    token = obtain_token()
    timer.time_counter('获取神策数据 token 后耗时：')
    conf = handle_contribution_config(contribution_config)
    # df = obtain_data_from_sa(token)
    # df_raw = tidy_data(df, contribution_config['target_join_property'])
    # df_summary = obtain_click_summary_data_from_sa(token)
    # df_result = calculate_contribution(df_raw=df_raw, df_summary=df_summary, contribution_type='last', conf=conf)
    # df_result.to_csv('~/Downloads/contribution_result1.csv', encoding='GB18030')
    df = pd.read_csv('~/Downloads/funmart_raw_data.csv', low_memory=False)
    timer.time_counter('读取 csv 文件后已耗时：')
    df_raw = tidy_data(df, contribution_config['target_join_property'])
    df_summary = obtain_click_summary_data_from_sa(token)
    df_result = calculate_contribution(df_raw=df_raw, df_summary=df_summary, conf=conf)
    # df_result. ('~/Downloads/contribution_result.csv', encoding='GB18030')
    
    add_condition_format('/Users/GavinXue/Downloads/pandas_conditional.xlsx', df_result, conf=conf)
