#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import cfg
from framework import fwk
from market import mkt
from logger import log
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime,timedelta
import pandas as pd
import talib as ta
import time

class Bbands():
    def __init__(self):
        self.up = pd.Series()
        self.mid = pd.Series()
        self.low = pd.Series()
        self.kl = pd.DataFrame()
        mkt.register_handle('kline', self.handle_data)


    def get_bands(self):
        while self.up.empty == True:
            log.info("waiting kline data!")
            time.sleep(1)
        return self.up, self.mid, self.low
        
    def get_last_band(self):
        while self.up.empty == True:
            log.info("get_last_band waiting kline data!")
            time.sleep(1)
        up = self.up[self.up.size-1]
        mid = self.mid[self.mid.size-1]
        low = self.low[self.low.size-1]
        return up,mid,low
        
    def handle_data(self, kl):
        log.dbg("handle kline data")
        self.kl = kl
        cp = kl['c']
        self.up, self.mid, self.low = ta.BBANDS(cp, timeperiod = 5, nbdevup = 2, nbdevdn = 2, matype = 0)
        
    def graphic(self):
        while self.kl.empty == True:
            log.info("waiting kline data!")
            time.sleep(1)
        cp = self.kl['c']
        t = self.kl['t']
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
        ax1.plot(cp, 'rd-', markersize=3)
        ax1.plot(self.up, 'y-')
        ax1.plot(self.mid, 'b-')
        ax1.plot(self.low, 'y-')
        ax1.set_title("bbands", fontproperties="SimHei")
        plt.show()

#bbands = Bbands()

class Macd():
    def __init__(self):
        self.macd = pd.Series()
        self.signal = pd.Series()
        self.hist = pd.Series()
        self.kl = pd.DataFrame()
        mkt.register_handle('kline', self.handle_data)


    def handle_data(self, kl):
        log.dbg("handle kline data")
        print(kl)
        self.kl = kl
        cp = kl['c']
        self.macd, self.signal, self.hist = ta.MACD(cp, fastperiod = 6, slowperiod = 12, signalperiod = 9)

    def graphic(self):
        while self.macd.empty == True:
            log.info("waiting macd data!")
            time.sleep(1)
        cp = self.kl['c']
        t = self.kl['t']
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
        ax1.plot(cp, 'rd-', markersize=3)
        ax1.plot(self.macd, 'y-')
        ax1.plot(self.signal, 'b-')
        ax1.plot(self.hist, 'y-')
        ax1.set_title("macd", fontproperties="SimHei")
        plt.show()

macd = Macd()

if __name__ == '__main__':
    mkt.start()
    #bbands.graphic()
    macd.graphic()
    mkt.stop()
    
