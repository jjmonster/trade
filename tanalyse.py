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
        self.data = pd.DataFrame()
        self.kl = pd.DataFrame()
        mkt.register_handle('kline', self.handle_data)


    def get_bands(self):
        while self.data.empty == True:
            log.info("waiting kline data!")
            time.sleep(1)
        return self.data['up'], self.data['mid'], self.data['low']
        
    def get_last_band(self):
        while self.data.empty == True:
            log.info("get_last_band waiting data!")
            time.sleep(1)
        last_row = self.data.iloc[-1] #or irow(-1)?
        return last_row[0], last_row[1], last_row[2]
        
    def handle_data(self, kl):
        log.dbg("handle kline data")
        self.kl = kl
        cp = kl['c']
        self.data['up'], self.data['mid'], self.data['low'] = ta.BBANDS(cp, timeperiod = 5, nbdevup = 2, nbdevdn = 2, matype = 0)
        
    def graphic(self):
        while self.data.empty == True:
            log.info("waiting bbands data!")
            time.sleep(1)
        cp = self.kl['c']
        t = list(map(datetime.fromtimestamp, self.kl['t']))
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
        ax1.plot(t, cp, 'rd-', markersize=3)
        ax1.plot(t, self.data['up'], 'y-')
        ax1.plot(t, self.data['mid'], 'b-')
        ax1.plot(t, self.data['low'], 'y-')
        ax1.set_title("bbands", fontproperties="SimHei")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
        ax1.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
        plt.xticks(rotation=45)
        plt.legend()
        plt.show()

bbands = Bbands()

class Macd():
    def __init__(self):
        self.data = pd.DataFrame()
        self.kl = pd.DataFrame()
        mkt.register_handle('kline', self.handle_data)

    def get_macd(self):
        while self.data.empty == True:
            log.info("waiting kline data!")
            time.sleep(1)
        return self.data['macd'], self.data['signal'], self.data['hist']

    def get_last_macd(self):
        while self.data.empty == True:
            log.info("get_last_band waiting data!")
            time.sleep(1)
        last_row = self.data.iloc[-1] #or irow(-1)?
        return last_row[0], last_row[1], last_row[2]

    def handle_data(self, kl):
        log.dbg("handle kline data")
        self.kl = kl
        cp = kl['c']
        #DIF DEA 
        self.data['macd'], self.data['signal'], self.data['hist'] = ta.MACD(cp, fastperiod = 12, slowperiod = 26, signalperiod = 9) #12 26 9 / 6 12 9

    def graphic(self):
        while self.data.empty == True:
            log.info("waiting macd data!")
            time.sleep(1)
        cp = self.kl['c']
        t = list(map(datetime.fromtimestamp, self.kl['t']))
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
        #ax1.plot(cp, 'rd-', markersize=3) #don't plot price
        ax1.plot(t, self.data['macd'], 'y-')
        ax1.plot(t, self.data['signal'], 'b-')
        ax1.plot(t, self.data['hist'], 'g-')
        ax1.set_title("macd", fontproperties="SimHei")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
        ax1.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
        plt.xticks(rotation=45)
        plt.legend()
        plt.show()

macd = Macd()

if __name__ == '__main__':
    mkt.start()
    bbands.graphic()
    macd.graphic()
    mkt.stop()
    
