# -*- coding: utf-8 -*-
"""
Created on 2016/12/9 16:45

@version: python3.5
@author: qiding

@files_in:
\\\\SHIMING\\trading\\holding_files\\7\\holding_evening\\today_str_trading.xls
\\\\SHIMING\\trading\\holding_files\\7\\holding_evening\\today_str_holding.xls
\\\\SHIMING\\trading\\target_files\\7\\today_str_final_stock.csv
E:\\MyTrading\\IntradayAccount\\Account\\No7DailyAccount\\adj_data.csv

@files_out:
E:\\MyTrading\\IntradayAccount\\Account\\No7DailyAccount\\trade.csv
E:\\MyTrading\\IntradayAccount\\Account\\No7DailyAccount\\holding.csv
E:\\MyTrading\\IntradayAccount\\Account\\No7DailyAccount\\trade_next_day_N07_today_str.csv
"""

import my_path
import datetime
import pandas as pd
import numpy as np
import os
import log

my_log = log.my_log


def read_trading_data(today_path, today_str):
    # read trading data
    trading_file_path1 = my_path.no_7_shiming_path + today_str + '_trading.xls'
    trading_file_path2 = today_path + 'trade.csv'

    trade_s_tmp = ''
    with open(trading_file_path1, 'r') as f_in:
        for line in f_in:
            line = line.replace("=", "").replace('"', "").replace('\t', ',')
            trade_s_tmp += line
    if not os.path.exists(today_path):
        print('make dirs: {}'.format(today_path))
        os.makedirs(today_path)
    with open(trading_file_path2, 'w') as f_out:
        f_out.write(trade_s_tmp)

    trading_data_raw = pd.read_csv(trading_file_path2, encoding='gbk').rename(
        columns={'证券代码': 'coid', '操作': 'direction_c', '成交数量': 'volume'}
    )
    trading_data_raw['direction'] = trading_data_raw['direction_c'].apply(lambda x: {'证券买入': 1, '证券卖出':-1}[x])
    trading_data_raw['coid'] = trading_data_raw['coid'].apply(lambda x: str(x).zfill(6))

    trading_data = trading_data_raw[['coid', 'volume', 'direction']]
    trading_data['trade_today'] = trading_data['volume'] * trading_data['direction']

    trading_data_agg = trading_data.groupby('coid', as_index=False)['trade_today'].sum()
    trading_data_agg = trading_data_agg[trading_data_agg['trade_today'] != 0]
    trading_data_agg['trade_today'] /= 100

    return trading_data, trading_data_agg


def read_holding_data(today_path, today_str):
    # read trading data
    trading_file_path1 = my_path.no_7_shiming_path + today_str + '_holding.xls'
    trading_file_path2 = today_path + 'holding.csv'

    trade_s_tmp = ''
    with open(trading_file_path1, 'r') as f_in:
        for line in f_in:
            line = line.replace("=", "").replace('"', "").replace('\t', ',')
            trade_s_tmp += line
    if not os.path.exists(today_path):
        print('make dirs: {}'.format(today_path))
        os.makedirs(trading_file_path2)
    with open(trading_file_path2, 'w') as f_out:
        f_out.write(trade_s_tmp)

    trading_data_raw = pd.read_csv(trading_file_path2, encoding='gbk').rename(
        columns={'证券代码': 'coid', '当前持仓': 'holding'}
    )
    trading_data_raw['coid'] = trading_data_raw['coid'].apply(lambda x: str(x).zfill(6))

    trading_data = trading_data_raw[['coid', 'holding']]

    trading_data['holding'] /= 100

    return trading_data


def read_target_data(today_str, today_path):
    # read target
    final_stock_path_root = my_path.final_stock_path_no_7
    final_stock_file_name = [
        file_name_tmp
        for file_name_tmp in os.listdir(final_stock_path_root)
        if file_name_tmp.startswith('final_stock_'+today_str) and file_name_tmp.endswith('.csv')
        ]
    assert len(final_stock_file_name) == 1
    target_data = pd.read_csv(final_stock_path_root + final_stock_file_name[0]).rename(
        columns={'coid': 'coid', 'trade': 'trade_target'}
    )
    target_data['coid'] = target_data['coid'].apply(lambda x: str(x).zfill(6))
    target_data.to_csv(today_path + 'target_data.csv', index=False)
    return target_data


def get_adjust_data(today_path):
    adj_path = today_path + 'adj_data.csv'
    try:
        data = pd.read_csv(adj_path).rename(columns={'代码': 'coid', '股数': 'vol_adjust'})
        data = data[['coid', 'vol_adjust']]
        data['vol_adjust'] /= 100
    except OSError:
        print('adjust data not found, use None replace')
        data = pd.DataFrame(columns=['coid', 'vol_adjust'])
        # coid = [600113, 600872]
        # amt = [-50, -54]
        # data = pd.DataFrame([coid, amt], index=['coid', 'vol_adjust']).T
    data['coid'] = data['coid'].apply(lambda x: str(x).zfill(6))
    return data


def main():
    today = datetime.datetime.now()
    today_str = today.strftime('%Y%m%d')

    this_path_root = my_path.output_path_no_7_daily_account
    today_path = this_path_root + today_str + '\\'
    
    my_log.add_path(today_path+'log.log')
    
    my_log.info('today_str: {}'.format(today_str))
    my_log.info('today path: {}'.format(today_path))
    shiming_path_output = my_path.no_7_shiming_path_output

    _, trading_data = read_trading_data(today_path, today_str)
    my_log.info('trading data len: {}'.format(len(trading_data)))

    target_data = read_target_data(today_str=today_str, today_path=today_path)
    my_log.info('target data len: {}'.format(len(target_data)))

    adjust_data = get_adjust_data(today_path)
    my_log.info('adjust data len: {}'.format(len(adjust_data)))

    holding_data = read_holding_data(today_str=today_str, today_path=today_path)

    data_merge_0 = pd.merge(left=target_data, right=trading_data, on='coid', how='outer').fillna(0).sort_values('coid')
    data_merge_1 = pd.merge(data_merge_0, adjust_data, on='coid', how='outer').fillna(0).sort('coid')
    data_merge = pd.merge(data_merge_1, holding_data, on='coid', how='outer').fillna(0).sort('coid')
    data_merge['trade_tomorrow_raw'] = data_merge['trade_target'] - data_merge['trade_today'] + data_merge['vol_adjust']

    data_merge['trade_tomorrow'] = np.where(data_merge['trade_tomorrow_raw']+data_merge['holding']<0, -data_merge['holding'], data_merge['trade_tomorrow_raw'])
    data_merge.to_csv(today_path + 'data_merged.csv', index=False)
    my_log.info('data merge:\n{}'.format(data_merge.to_string()))

    trade_next_day = data_merge[['coid', 'trade_tomorrow']][data_merge['trade_tomorrow'].abs()>=1]
    my_log.info('trade next day:\n{}'.format(trade_next_day))

    my_log.info('trade next day path: {}'.format(today_path + 'trade_next_day_'+today_str+'.csv'))
    my_log.info('trade next day path: {}'.format(shiming_path_output + 'trade_next_day_N07_'+today_str+'.csv'))
    my_log.info('trade next day path: {}'.format(shiming_path_output + 'trade_next_day_N07_'+today_str+'.csv'))
    trade_next_day.to_csv(today_path + 'trade_next_day_N07_'+today_str+'.csv', index=False)
    trade_next_day.to_csv(shiming_path_output + 'trade_next_day_N07_'+today_str+'.csv', index=False)
    trade_next_day.rename(columns={'trade_tomorrow': 'trade'}).to_csv(shiming_path_output + 'trade_next_day_N07_'+today_str+'.csv', index=False)


if __name__ == '__main__':
    main()
