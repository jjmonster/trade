#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from collections import defaultdict
from utils import s2f

class config:
    def __init__(self, cfg_file):
        self.cf = cfg_file
        self.cfg = defaultdict(lambda: None)
        self.cfg_header = defaultdict(lambda: None)
        self.load_cfg_all()
        self.load_cfg_header()

    def set_cfg(self,key, val):
        self.cfg[key] = val

    def get_cfg(self,key):
        return self.cfg[key]

    def get_cfg_all(self):
        return self.cfg

    def get_cfg_file(self):
        return self.cf

    def get_cfg_header(self):
        return self.cfg_header

    def get_url(self):
        return self.cfg['base_url']

    def get_cfg_plat(self):
        """return platform name"""
        return self.cfg['base_url'].split('.')[1]

    def get_coin1(self):
        return self.cfg['coin1']

    def get_coin2(self):
        return self.cfg['coin2']

    def get_pair(self):
        plt = self.get_cfg_plat()
        if plt == 'okex' or plt == 'okcoin':
            if self.get_cfg('future_or_spot') == 'future':
                return self.cfg['coin1']+'_usd'
            else:
                return self.cfg['coin1']+'_'+self.cfg['coin2']
        else:
            return self.cfg['coin1']+self.cfg['coin2']

    def get_id(self):
        return self.cfg['id']
        
    def get_secretKey(self):
        return self.cfg['secret_key']

    def get_fee(self):
        return self.cfg['fee_percentage']

    def get_trans_fee(self):
        return self.cfg['trans_fee_percentage']

    def load_cfg_all(self):
        try:
            c = configparser.ConfigParser()
            c.read(self.cf, encoding="utf-8")
            for s in c.sections():
                dic = dict(c.items(s))
                self.cfg = s2f(dict(self.cfg, **dic))
        except:
            print("Fail parse config file '%s'!"%self.cf)
        return self.cfg

    def load_cfg_header(self):
        self.cfg_header = self.load_cfg_section("request_header")
        return self.cfg_header

    def load_cfg_section(self, section):
        try:
            c = configparser.ConfigParser()
            c.read(self.cf, encoding="utf-8")
            return dict(c.items(section))
        except:
            print("Fail parse config file '%s'!"%self.cf)

    def load_config(self):
        self.load_cfg_all()
        self.load_cfg_header()

    def print_cfg(self):
        print(self.cfg)

cfg = config("base.ini")
if __name__ == '__main__':
    """test"""
    print(cfg.get_cfg_all())
    print(cfg.get_cfg_header())
    print(cfg.get_cfg_plat())
    
    
