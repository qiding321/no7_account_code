# -*- coding: utf-8 -*-
"""
Created on 2016/12/9 9:59

@version: python3.5
@author: qiding
"""

import socket

name = socket.gethostname()

no_7_shiming_path = r'\\SHIMING\trading\holding_files\7\holding_evening' + '\\'
no_7_shiming_path_output = r'\\SHIMING\trading\target_files\7m' + '\\'

if name == '2013-20151201LG':
    output_path_root = r'E:\MyTrading\IntradayAccount\Account' + '\\'
    log_path = r'E:\MyTrading\IntradayAccount\Log\log.log'

    output_path_account_summary = output_path_root + 'IntradayAccountSummary' + '\\'

    output_path_no_7_daily_account = output_path_root + 'No7DailyAccount' + '\\'
    final_stock_path_no_7 = r'\\SHIMING\trading\target_files\7' + '\\'
