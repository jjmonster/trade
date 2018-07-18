#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from framework import frmwk
import threading
import time

class market:
    def __init__(self):
        self.fwk = frmwk()
        self.running = 0
        

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
            self.update_price()
            #self.update_balance()
            #self.update_depth()
            self.update_kline()
            
        
    def stop(self):
        self.running = 0
        self.p_timer.cancel()
        #self.b_timer.cancel()
        #self.d_timer.cancel()
        self.k_timer.cancel()

    def update_balance(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.balance = self.fwk.get_balance(pair)
        if self.running == 1:
            self.b_timer = threading.Timer(1, self.update_balance)
            self.b_timer.start()

    def update_price(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.price = self.fwk.get_price(pair)
        #print(self.price)
        if self.running == 1:
            self.p_timer = threading.Timer(1, self.update_price)
            self.p_timer.start()

    def update_depth(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.depth = self.fwk.get_market_depth(pair)
        #print(self.depth)
        if self.running == 1:
            self.d_timer = threading.Timer(1, self.update_depth)
            self.d_timer.start()

    def update_kline(self):
        pair = config.get_cfg("coin1")+config.get_cfg("coin2")
        self.kline = self.fwk.get_K_line(pair, limit=10, dtype="1day")
        #print(self.kline)
        if self.running == 1:
            self.k_timer = threading.Timer(10, self.update_kline)
            self.k_timer.start()



if __name__ == '__main__':
    #just for test
    config.load_cfg_all()
    m = market()
    m.start()
    time.sleep(10)
    m.stop()
