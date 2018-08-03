#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from config import cfg
from framework import fwk
from logger import log
import pandas as pd

import threading
import time



class market:
    def __init__(self):
        self.running = 0
        self.data_handles = defaultdict(lambda:[])
        self.pair = cfg.get_cfg("coin1")+cfg.get_cfg("coin2")
        self.price = 0
        self.balance = []
        self.depth = []
        self.kline = pd.DataFrame()

    def get_price(self):
        return self.price

    def get_balance(self):
        return self.balance

    def get_depth(self):
        return self.depth
        
    def get_kline(self):
        return self.kline
    

    def start(self):
        if self.running == 0:
            self.running = 1
            thread = threading.Thread(target=self._update_price, args=(1,))
            thread.start()
            
#            thread = threading.Thread(target=self._update_balance, args=(1,))
#            thread.start()
            
            thread = threading.Thread(target=self._update_depth, args=(1,))
            thread.start()
            
            thread = threading.Thread(target=self._update_kline, args=(3600,))
            thread.start()

        
    def stop(self):
        self.running = 0
        self._p_timer.cancel()
        #self._b_timer.cancel()
        self._d_timer.cancel()
        self._k_timer.cancel()

    def _update_balance(self, timeout):
        self.balance = fwk.get_balance(cfg.get_pair())
        if self.balance != None and len(self.balance) > 0:
            for h in self.data_handles['balance']:
                h(self.balance)
        if self.running == 1:
            self._b_timer = threading.Timer(timeout, self._update_balance, [timeout])
            self._b_timer.start()

    def _update_price(self, timeout):
        self.price = fwk.get_price(cfg.get_pair())
        #print(self.price)
        if self.price != None and len(self.price) > 0:
            for h in self.data_handles['price']:
                h(self.price)
        if self.running == 1:
            self._p_timer = threading.Timer(timeout, self._update_price, [timeout])
            self._p_timer.start()

    def _update_depth(self, timeout):
        self.depth = fwk.get_depth(cfg.get_pair())
        #print(self.depth)
        if self.depth != None and len(self.depth) > 0:
            for h in self.data_handles['depth']:
                h(self.depth)
        if self.running == 1:
            self._d_timer = threading.Timer(timeout, self._update_depth, [timeout])
            self._d_timer.start()

    def _update_kline(self, timeout):
        self.kline = fwk.get_kline(cfg.get_pair(), dtype="1hour", limit=100)
        for h in self.data_handles['kline']:
            h(self.kline)
        if self.running == 1:
            self._k_timer = threading.Timer(timeout, self._update_kline, [timeout])
            self._k_timer.start()

    def register_handle(self, dtype, func):
        log.dbg("register_handle %s %s"%(dtype, func))
        self.data_handles[dtype].append(func)

    def unregister_handle(self, dtype, func):
        log.dbg("unregister_handle %s %s"%(dtype, func))
        self.data_handles[dtype].remove(func)


mkt = market()
if __name__ == '__main__':
    #just for test
    mkt.start()
    time.sleep(10)
    mkt.stop()
