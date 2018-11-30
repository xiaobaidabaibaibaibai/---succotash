# -*- coding: utf-8 -*-
from resource_location_contribution import handle_contribution_config, obtain_data_from_sa, \
    tidy_data, obtain_click_summary_data_from_sa, calculate_contribution, add_condition_format, ScriptsTimer
from public_function import obtain_token
from send_email import send_email
from config import contribution_config, contri_email


def main():
    timer = ScriptsTimer()
    timer.start()
    
    token = obtain_token()
    timer.time_counter('获取神策环境 token 后已耗时：')
    
    conf = handle_contribution_config(contribution_config)
    df = obtain_data_from_sa(token)
    timer.time_counter('从神策环境获取后，已耗时：')
    
    df_raw = tidy_data(df, conf['target_join_property'])
    df_summary = obtain_click_summary_data_from_sa(token)
    timer.time_counter('数据准备、清洗完成后，已耗时：')
    
    df_result = calculate_contribution(df_raw=df_raw, df_summary=df_summary, conf=conf)
    add_condition_format(conf['result_file'], df_result, conf=conf)
    timer.time_counter('生成归因结果文件后，已耗时：')
    
    send_email(contri_email, conf['result_file'])
    timer.time_counter('归因邮件发送完成，总耗时：')
    timer.end()
    

if __name__ == '__main__':
    main()
