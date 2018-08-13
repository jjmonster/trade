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


def get_df_data(df):
    while df.empty == True:
        log.info("get_df_data waiting data!")
        time.sleep(1)
    return df
    
def get_df_data_timestamp(df, timestamp):
    while df.empty == True:
        log.info("get_df_data_timestamp waiting data!")
        time.sleep(1)
    t = df['t']
    for i in range(t.size -1):
        if t[i] <= timestamp and t[i+1] > timestamp:
            row = i
    if t[i+1] <= timestamp:
        row = i+1
    return df.iloc[row]

def get_df_data_last(df):
    while df.empty == True:
        log.info("get_df_data_last waiting data!")
        time.sleep(1)
    return df.iloc[-1] #or irow(-1)?


def _graphic(df, title):
    fig = plt.figure(figsize=(12,8))
    ax1= fig.add_subplot(111)
    line_color = ('b','g','r','c','m','y','k','w')
    line_maker = ('.',',','o') ###...
    line_style = ('-', '--', '-.', ':')

    t = list(map(datetime.fromtimestamp, df['t']))
    for i in range(df.columns.size): #exclude 't'
        if df.columns[i] == 't':
            continue
        column = df[df.columns[i]]
        ax1.plot(t, column, line_color[i]+line_style[0])

    ax1.set_title(title, fontproperties="SimHei")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
    ax1.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()


class Bbands():
    def __init__(self):
        self.data = pd.DataFrame()
        self.kl = pd.DataFrame()
        mkt.register_handle('kline', self.handle_data)

    def get_bands(self):
        return get_df_data(self.data)

    def get_band_timestamp(self, timestamp):
        row_data = get_df_data_timestamp(self.data, timestamp)
        return row_data['up'], row_data['low']
        
    def get_last_band(self):
        last_row = get_df_data_last(self.data)
        return last_row['up'], last_row['low']
        
    def handle_data(self, kl):
        self.kl = kl
        self.data['t'] = kl['t']
        #MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
        self.data['up'], self.data['ma'], self.data['low'] = ta.BBANDS(kl['c'], timeperiod = 10, nbdevup = 1.5, nbdevdn = 1.5, matype = 0)

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
        df = pd.DataFrame()
        df['c'] = self.kl['c']
        df['t'] = self.kl['t']
        df['up'] = self.data['up']
        df['low'] = self.data['low']
        #df['ma'] = self.data['ma'] ##use other ma, no need this
        #x,y = self.coordinate_repeat(t, self.data['up'])
        #x,y = self.coordinate_repeat(t, self.data['low'])
        _graphic(df, "bbands")

class MaClass():
    def __init__(self, type, timeperiod):
        self.data = pd.DataFrame()
        self.kl = pd.DataFrame()
        self.type = type
        self.timeperiod = timeperiod
        mkt.register_handle('kline', self.handle_data)

    def get_data(self):
        return get_df_data(self.data)

    def get_data_timestamp(self, timestamp):
        row_data = get_df_data_timestamp(self.data, timestamp)
        return row_data['real']

    def get_last_data(self):
        last_row = get_df_data_last(self.data)
        return last_row['real']

    def handle_data(self, kl):
        self.kl = kl
        self.data['t'] = kl['t']
        if self.type == 'ma':
            self.data['real'] = ta.MA(kl['c'], timeperiod = self.timeperiod)
        elif self.type == 'wma':
            self.data['real'] = ta.WMA(kl['c'], timeperiod = self.timeperiod)
        elif self.type == 'sma':
            self.data['real'] = ta.SMA(kl['c'], timeperiod = self.timeperiod)
        elif self.type == 'ema':
            self.data['real'] = ta.EMA(kl['c'], timeperiod = self.timeperiod)
        elif self.type == 'dema':
            self.data['real'] = ta.DEMA(kl['c'], timeperiod = self.timeperiod)
        elif self.type == 'trima':
            self.data['real'] = ta.TRIMA(kl['c'], timeperiod = self.timeperiod)
        elif self.type == 'kama':
            self.data['real'] = ta.KAMA(kl['c'], timeperiod = self.timeperiod)
        elif self.type == 't3':
            self.data['real'] = ta.KAMA(kl['c'], timeperiod = self.timeperiod, vfactor = 0)
        else:
            log.err("haven't implement ma type:%s"%(self.type))

    def graphic(self):
        while self.data.empty == True:
            log.info("waiting MA data!")
            time.sleep(1)
        df = pd.DataFrame()
        df['c'] = self.kl['c']
        df['t'] = self.kl['t']
        df['real'] = self.data['real']
        _graphic(df, self.type)

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


kama = MaClass('kama', 10)
sma_fast = MaClass('sma', 5)
sma_slow = MaClass('sma', 10)
bbands = Bbands()
macd = Macd()

def df_mix(*df):
    data = df[0]
    if len(df) > 1:
        for i in range(len(df)-1):
            data = pd.merge(data, df[i+1], how='left', on='t')
    return data

if __name__ == '__main__':
    #bbands.graphic()
    #macd.graphic()
    kama.graphic()
    #up,low = bbands.get_band_timestamp(1533968011)
    #print(up, low)

    #df = df_mix(sma_fast.get_data().rename(columns={'real':'fast'}), sma_slow.get_data().rename(columns={'real':'slow'}))
    #_graphic(df, 'mixed')
    mkt.stop()

    
