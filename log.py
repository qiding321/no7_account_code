# -*- coding: utf-8 -*-
"""
Created on 2016/12/9 13:00

@version: python3.5
@author: qiding
"""

import logging
import my_path

class Logger(logging.Logger):
    def add_path(self, add_path):
        this_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        handler_file = logging.FileHandler(add_path)
        handler_file.setFormatter(this_formatter)
        self.addHandler(handler_file)
        self.info('add path: {}'.format(add_path))


my_log = Logger(name='log', level='INFO')

this_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler_file = logging.FileHandler(my_path.log_path)
handler_file.setFormatter(this_formatter)

handler_console = logging.StreamHandler()
handler_console.setLevel(logging.INFO)
handler_console.setFormatter(this_formatter)

my_log.addHandler(handler_console)
my_log.addHandler(handler_file)

my_log.info('log begin: {}'.format(my_path.log_path))