#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from config import cfg
from framework import fwk
from logger import log
import pandas as pd
import threading
import time
from signalslot import sslot

class market:
    def __init__(self):
        self.days = 10
        self.data_handles = {
            'price':{'thandle':None, 'tfunc':self._update_price, 'tperiod':10, 'data':0, 'func':[], 'reg':0},
            #'balance':{'thandle':None, 'tfunc':self._update_balance, 'tperiod':10, 'data':[], 'func':[], 'reg':0},
            'depth':{'thandle':None, 'tfunc':self._update_depth, 'tperiod':1, 'data':[], 'func':[], 'reg':0},
            'kline':{'thandle':None, 'tfunc':self._update_kline, 'tperiod':3600, 'data':pd.DataFrame(), 'func':[], 'reg':0},
        } ##defaultdict(lambda:[])
        sslot.register_plat_select(self._update_kline_without_timer)
        sslot.register_pair_select(self._update_kline_without_timer)
      
    def get_price(self):
        return self.data_handles['price']['data']

    def get_balance(self):
        return self.data_handles['balance']['data']

    def get_depth(self):
        return self.data_handles['depth']['data']
        
    def get_kline(self):
        return self.data_handles['kline']['data']

    def _update_balance(self):
        handles = self.data_handles['balance']
        handles['data'][0] = fwk.get_balance(cfg.get_coin1())
        handles['data'][1] = fwk.get_balance(cfg.get_coin2())
        if handles['data'] != None and len(handles['data']) > 0:
            for f in handles['func']:
                f(handles['data'])
        if handles['reg'] > 0:
            handles['thandle'] = threading.Timer(handles['tperiod'], handles['tfunc'])
            handles['thandle'].start()


    def _update_price(self):
        handles = self.data_handles['price']
        handles['data'] = fwk.get_price(cfg.get_pair())
        if handles['data'] != None and len(handles['data']) > 0:
            for f in handles['func']:
                f(handles['data'])
        if handles['reg'] > 0:
            handles['thandle'] = threading.Timer(handles['tperiod'], handles['tfunc'])
            handles['thandle'].start()

    def _update_depth(self):
        handles = self.data_handles['depth']
        #t1 = time.time()
        handles['data'] = fwk.get_depth(cfg.get_pair())
        t = time.time()
        #print(int(t-t1)) #time consume 
        if handles['data'] != None and len(handles['data']) > 0:
            for f in handles['func']:
                f(t, handles['data'])
        if handles['reg'] > 0:
            handles['thandle'] = threading.Timer(handles['tperiod'], handles['tfunc'])
            handles['thandle'].start()

    def _update_kline(self):
        handles = self.data_handles['kline']
        handles['data'] = fwk.get_kline(cfg.get_pair(), dtype="1hour", limit=min(self.days*24, 2000))
        #print("_update_kline", handles['data'])
        if handles['data'].size > 0:
            for f in handles['func']:
                f(handles['data'])
        else: ##fail get kline
            handles['thandle'] = threading.Timer(1, handles['tfunc'])
            handles['thandle'].start()
            return
        if handles['reg'] > 0:
            period = handles['tperiod'] - int(time.time())%handles['tperiod'] + 1 #local time currently, will use server time to improve
            handles['thandle'] = threading.Timer(period, handles['tfunc'])
            handles['thandle'].start()

    def _update_kline_without_timer(self, *notuse):
        handles = self.data_handles['kline']
        handles['data'] = fwk.get_kline(cfg.get_pair(), dtype="1hour", limit=min(self.days*24, 2000))
        if handles['data'].size > 0:
            for f in handles['func']:
                f(handles['data'])

    def register_handle(self, dtype, func):
        log.dbg("register_handle %s %s"%(dtype, func))
        handles = self.data_handles[dtype]
        if func in handles['func']:
            log.war(" %s already handled!"%(func))
            return
        #as kline have long period, the newly obj callback func can't been called immediately.
        #so call it when first register.
        if dtype == 'kline' and handles['data'].size > 0:
            func(handles['data'])
        handles['func'].append(func)
        handles['reg'] += 1
        #print("register_handle", handles)
        if handles['reg'] == 1:
            handles['thandle'] = threading.Timer(1, handles['tfunc']) #first start timer 1s period
            handles['thandle'].start()

    def unregister_handle(self, dtype, func):
        log.dbg("unregister_handle %s %s"%(dtype, func))
        handles = self.data_handles[dtype]
        if func in handles['func']:
            handles['func'].remove(func)
            handles['reg'] -= 1
            if handles['reg'] == 0:
                handles['thandle'].cancel()

    def stop(self):
        for v in self.data_handles.values():
            if v['reg'] > 0:
                v['thandle'].cancel()
                v['func'].clear()
                v['reg'] = 0


mkt = market()
def test_callback(data):
    print(data)
if __name__ == '__main__':
    #just for test
    mkt.register_handle('kline', test_callback)
    time.sleep(10)
    mkt.unregister_handle('kline', test_callback)
