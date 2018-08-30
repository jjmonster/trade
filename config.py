#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from collections import defaultdict
from utils import s2f
from signalslot import sslot

class config:
    def __init__(self, cfg_file):
        self.cf = cfg_file
        self.cp = configparser.ConfigParser()
        self.cp.read(cfg_file, encoding="utf-8")

        sslot.register_plat_select(self.set_url)
        sslot.register_pair_select(self.set_pair)
        sslot.register_indicator_select(self.set_indicator)

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

    def set_url(self, platform):
        if platform == 'okex':
            self.cp.set('base', 'base_url', 'https://www.okex.com')
        elif platform == 'okcoin':
            self.cp.set('base', 'base_url', 'https://www.okcoin.com')
        elif platform == 'coinex':
            self.cp.set('base', 'base_url', 'https://api.coinex.com/v1')
        self.set_cfg_header()

    def get_cfg_plat(self):
        return self.get_url().split('.')[1]

    def get_cfg_header(self):
        return self.get_cfg_section('request_header')

    def set_cfg_header(self):
        plt = self.get_cfg_plat()
        if plt == 'okex' or plt == 'okcoin':
            for o in self.cp.options('request_header'):
                self.cp.remove_option('request_header', o)
            self.cp.set('request_header', 'Content-Type', 'application/x-www-form-urlencoded')
        elif plt == 'coinex':
            for o in self.cp.options('request_header'):
                self.cp.remove_option('request_header', o)
            self.cp.set('request_header','Content-Type','application/json')
            self.cp.set('request_header','User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
            self.cp.set('request_header','authorization','')
            
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

    def set_coin1(self, val):
        self.set_cfg('coin1', val)

    def get_coin2(self):
        return self.get_cfg_item('misc','coin2')

    def set_coin2(self, val):
        self.set_cfg('coin2', val)

    def get_pair(self):
        plt = self.get_cfg_plat()
        if plt == 'okex' or plt == 'okcoin':
            if self.is_future():
                return self.get_coin1()+'_usd'
            else:
                return self.get_coin1()+'_'+self.get_coin2()
        else:
            return self.get_coin1()+self.get_coin2()

    def set_pair(self, pair):
        try:
            coins = pair.split('_')
            self.set_coin1(coins[0])
            self.set_coin2(coins[1])
        except:
            log.err("fail set pair! %s"%pair)
        
    def get_indicator(self):
        return self.get_cfg_item('misc','indicator')

    def set_indicator(self, val):
        self.set_cfg('indicator', val)

    def get_fee(self):
        return self.get_cfg_item('misc','fee_percentage', 'float')

    def get_trans_fee(self):
        return self.get_cfg_item('misc','trans_fee_percentage', 'float')

    def print_cfg(self):
        print(self.get_cfg_all())

cfg = config("base.ini")
if __name__ == '__main__':
    """test"""
    print(cfg.get_cfg_all())
    print(cfg.get_cfg_header())
    print(cfg.get_cfg_plat())
    print(cfg.get_pair())
    print(cfg.get_id())
    cfg.set_url("okcoin")
    print(cfg.get_cfg_header())
    cfg.set_pair("aaa_bbb")
    print(cfg.get_pair())
    #cfg.write_file()

    
