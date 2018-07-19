#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from framework import frmwk
import threading
import time
from collections import defaultdict


class market:
    def __init__(self):
        self._fwk = frmwk()
        self.running = 0
        self.data_handles = defaultdict(lambda:[])
        

    def get_price(self):
        while len(self.price) == 0:
            print("waiting to get price...")
            #print(self.price)
            time.sleep(1)
        return self.price

    def get_balance(self):
        while len(self.balance) == 0:
            print("waiting to get balance...")
            time.sleep(1)
        return self.balance

    def get_depth(self):
        while len(self.depth) == 0:
            print("waiting to get depth...")
            print(self.depth)
            time.sleep(1)
        return self.depth
        
    def get_kline(self):
        while len(self.kline) == 0:
            print("waiting to get depth...")
            print(self.kline)
            time.sleep(1)
        return self.kline
    

    def start(self):
        if self.running == 0:
            self.running = 1
            self._update_price()
            #self._update_balance()
            self._update_depth()
            self._update_kline()
            
        
    def stop(self):
        self.running = 0
        self._p_timer.cancel()
        #self._b_timer.cancel()
        self._d_timer.cancel()
        self._k_timer.cancel()

    def _update_balance(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.balance = self._fwk.get_balance(pair)
        if len(self.balance) > 0:
            for h in self.data_handles['balance']:
                h(self.balance)
        if self.running == 1:
            self._b_timer = threading.Timer(1, self._update_balance)
            self._b_timer.start()

    def _update_price(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.price = self._fwk.get_price(pair)
        #print(self.price)
        if len(self.price) > 0:
            for h in self.data_handles['price']:
                h(self.price)
        if self.running == 1:
            self._p_timer = threading.Timer(1, self._update_price)
            self._p_timer.start()

    def _update_depth(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.depth = self._fwk.get_market_depth(pair)
        #print(self.depth)
        if len(self.depth) > 0:
            for h in self.data_handles['depth']:
                h(self.depth)
        if self.running == 1:
            self._d_timer = threading.Timer(1, self._update_depth)
            self._d_timer.start()

    def _update_kline(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.kline = self._fwk.get_K_line(pair, limit=10, dtype="1day")
        #print(self.kline)
        if len(self.kline) > 0:
            for h in self.data_handles['kline']:
                h(self.kline)
        if self.running == 1:
            self._k_timer = threading.Timer(3600, self._update_kline)
            self._k_timer.start()

    def register_handle(self, dtype, func):
        self.data_handles[dtype].append(func)

    def unregister_handle(self, dtype, func):
        self.data_handles[dtype].remove(func)


if __name__ == '__main__':
    #just for test
    config.load_cfg_all()
    m = market()
    m.start()
    time.sleep(10)
    m.stop()
