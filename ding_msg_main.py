# -*- coding: utf-8 -*-
from public_function import obtain_data_from_url,storage_excel_saved,DingDingPMSRobot_MSG_send
import time

def main():
    sql_result = obtain_data_from_url()
    storage_excel_saved(sql_result, 'D://BaiduNetdiskDownload/')
    #DingDingPMSRobot_MSG_send('file_path', '/n你有一份特别的快递！', 'mobilephone_num')

if __name__ == '__main__':
    main()