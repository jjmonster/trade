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
import numpy as np
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
        return self.data['up'], self.data['low'], self.data['ma10'], self.data['ma20']
        
    def get_last_band(self):
        while self.data.empty == True:
            log.info("get_last_band waiting data!")
            time.sleep(1)
        last_row = self.data.iloc[-1] #or irow(-1)?
        return last_row['up'], last_row['low'], last_row['ma10'], last_row['ma20']
        
    def handle_data(self, kl):
        self.kl = kl
        cp = kl['c']
        #MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
        self.data['up'], self.data['ma5'], self.data['low'] = ta.BBANDS(cp, timeperiod = 5, nbdevup = 1, nbdevdn = 1, matype = 0)
        self.data['ma10'] = ta.MA(cp, 10)
        self.data['ma20'] = ta.MA(cp, 20)
        log.info("bband handle kline data up=%f, low=%f, ma10=%f, ma20=%f"%(self.get_last_band()))

    def coordinate_repeat(self, x, y): ##polygonal line
        arr1 = list(np.array(x).repeat(2))
        arr2 = list(np.array(y).repeat(2))
        arr1.pop(0)
        arr2.pop(-1)
        return pd.Series(arr1), pd.Series(arr2)
        
    def graphic(self):
        while self.data.empty == True:
            log.info("waiting bbands data!")
            time.sleep(1)
        cp = self.kl['c']
        t = list(map(datetime.fromtimestamp, self.kl['t']))
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
        ax1.plot(t, cp, 'rd-', markersize=3)
        x,y = self.coordinate_repeat(t, self.data['up'])
        ax1.plot(x, y, 'y-')
        x,y = self.coordinate_repeat(t, self.data['low'])
        ax1.plot(x, y, 'y-')

        ax1.plot(t, self.data['ma5'], 'b-')
        ax1.plot(t, self.data['ma10'], 'g-')
        ax1.plot(t, self.data['ma20'], 'k-')

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
        return self.data['dif'], self.data['dea'], self.data['macd'] 

    def get_last_macd(self):
        while self.data.empty == True:
            log.info("get_last_band waiting data!")
            time.sleep(1)
        last_row = self.data.iloc[-1] #or irow(-1)?
        return last_row[0], last_row[1], last_row[2]

    def analyse(self):
        signal = []
        dif, dea, macd = self.get_macd()
        for i in range(dif.size):
            val = dif[i] - dea[i]
            if abs(val) < 0.001:
                signal.append(0)
            else:
                if val > 0 and dea[i] > 0:
                    signal.append(0.5) #
                elif val < 0 and dif[i] < 0:
                    signal.append(-0.5) #
                else:
                    signal.append(0)
        return signal
        

    def handle_data(self, kl):
        log.dbg("handle kline data")
        self.kl = kl
        cp = kl['c']
        #SMA EMA WMA DEMA TEMA TRIMA KAMA MAMA T3 , MACDEXT
        #macd signal hist --> DIF DEA MACD , len(cp) > slowperiod*3
        self.data['dif'], self.data['dea'], self.data['macd'] = ta.MACD(cp, fastperiod = 12, slowperiod = 26, signalperiod = 9) #12 26 9 / 6 12 9
        #print(self.data)

    def graphic(self):
        while self.data.empty == True:
            log.info("waiting macd data!")
            time.sleep(1)
        cp = self.kl['c']
        t = list(map(datetime.fromtimestamp, self.kl['t']))
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
        ax1.plot(t, cp - cp.mean(), 'rd-', markersize=3) #price fixed around 0 for trend analyse
        ax1.plot(t, self.data['dif'], 'y-')
        ax1.plot(t, self.data['dea'], 'b-')
        #ax1.plot(t, self.data['macd'], 'g-')##bar, not need
        sig = pd.Series(self.analyse(), name='sig')
        #ax1.plot(t, sig, 'r-')  #trading signal
        ax1.plot(t, [0]*cp.size, 'r-') ##zero axis line
        ax1.set_title("macd", fontproperties="SimHei")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
        ax1.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
        plt.xticks(rotation=45)
        plt.legend()
        plt.show()

macd = Macd()

if __name__ == '__main__':
    bbands.graphic()
    #macd.graphic()
    mkt.stop()

    
