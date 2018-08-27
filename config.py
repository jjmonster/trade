#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from collections import defaultdict
from utils import s2f

class config:
    def __init__(self, cfg_file):
        self.cf = cfg_file
        self.cp = configparser.ConfigParser()
        self.cp.read(cfg_file, encoding="utf-8")

    def write_file(self):
        with open(self.cf, 'w') as f:
            self.cp.write(f)
        f.close()

    def set_cfg(self, option, val):
        for s in self.cp.sections():
            if self.cp.has_option(s, option):
                self.cp.set(s, option, val)

    def get_cfg(self, option):
        for s in self.cp.sections():
            if self.cp.has_option(s, option):
                return self.cp.get(s, option)

    def get_cfg_all(self):
        cfg_all = {}
        for s in self.cp.sections():
            items = dict(self.cp.items(s))
            cfg_all = s2f(dict(cfg_all, **items))
        return cfg_all

    def get_cfg_section(self, section):
        return dict(self.cp.items(section))

    def get_cfg_item(self, section, option, *type):
        t = 'str'
        if len(type) > 0:
            t = type[0]
        if t == 'int':
            var = self.cp.getint(section, option)
        elif t == 'float':
            var = self.cp.getfloat(section, option)
        elif t == 'boolean':
            var = self.cp.getboolean(section, option)
        else:
            var = self.cp.get(section, option)
        return var


    def get_url(self):
        return self.get_cfg_item('base', 'base_url')

    def get_cfg_plat(self):
        return self.get_url().split('.')[1]

    def get_cfg_header(self):
        return self.get_cfg_section('request_header')

    def get_id(self):
        return self.get_cfg_item('account','id')

    def get_secretKey(self):
        return self.get_cfg_item('account','secret_key')

    def is_future(self):
        return True if cfg.get_cfg_item('misc', 'future_or_spot') == 'future' else False

    def get_future_contract_type(self):
        return self.get_cfg_item('misc','future_contract_type')

    def get_coin1(self):
        return self.get_cfg_item('misc','coin1')

    def get_coin2(self):
        return self.get_cfg_item('misc','coin2')

    def get_pair(self):
        plt = self.get_cfg_plat()
        if plt == 'okex' or plt == 'okcoin':
            if self.is_future():
                return self.get_coin1()+'_usd'
            else:
                return self.get_coin1()+'_'+self.get_coin2()
        else:
            return self.get_coin1()+self.get_coin2()

    def get_indicator(self):
        return self.get_cfg_item('misc','indicator')

    def get_fee(self):
        return self.get_cfg_item('misc','fee_percentage', 'float')

    def get_trans_fee(self):
        return self.get_cfg_item('misc','trans_fee_percentage', 'float')

    def print_cfg(self):
        print(self.get_cfg_all)

cfg = config("base.ini")
if __name__ == '__main__':
    """test"""
    print(cfg.get_cfg_all())
    print(cfg.get_cfg_header())
    print(cfg.get_cfg_plat())
    print(cfg.get_pair())
    print(cfg.get_id())
    print(cfg.get_trans_fee())
    cfg.set_cfg('trans_fee_percentage', '0.9999')
    print(cfg.get_trans_fee())
    cfg.write_file()

    
