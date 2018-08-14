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

def df_merge(*df):
    data = df[0]
    if len(df) > 1:
        for i in range(len(df)-1):
            data = pd.merge(data, df[i+1], how='left', on='t')
    return data

def coordinate_repeat(x, y): ##polygonal line
    arr1 = list(np.array(x).repeat(2))
    arr2 = list(np.array(y).repeat(2))
    arr1.pop(0)
    arr2.pop(-1)
    return pd.Series(arr1), pd.Series(arr2)

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
    sig = pd.Series(self.analyse(), name='sig')


class  TechnicalAnalysis():
    def __init__(self, func, columns, **params):
        self.data = pd.DataFrame()
        self.kl = pd.DataFrame()
        self.func = func
        self.col = columns
        self.params = params
        mkt.register_handle('kline', self.handle_data)

    def get_data(self):
        return get_df_data(self.data)

    def get_data_timestamp(self, timestamp):
        return get_df_data_timestamp(self.data, timestamp)

    def get_last_data(self):
        return get_df_data_last(self.data)

    def handle_data(self, kl):
        if kl.empty == True:
            return
        self.kl = kl
        self.data['t'] = kl['t']
        if self.func == 'ma':
            #MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
            self.data[self.col[0]] = ta.MA(kl['c'], **self.params)
        elif self.func == 'wma':
            self.data[self.col[0]] = ta.WMA(kl['c'], **self.params)
        elif self.func == 'sma':
            self.data[self.col[0]] = ta.SMA(kl['c'], **self.params)
        elif self.func == 'ema':
            self.data[self.col[0]] = ta.EMA(kl['c'], **self.params)
        elif self.func == 'dema':
            self.data[self.col[0]] = ta.DEMA(kl['c'], **self.params)
        elif self.func == 'trima':
            self.data[self.col[0]] = ta.TRIMA(kl['c'], **self.params)
        elif self.func == 'kama':
            self.data[self.col[0]] = ta.KAMA(kl['c'], **self.params)
        elif self.func == 't3':
            self.data[self.col[0]] = ta.KAMA(kl['c'], **self.params)##, vfactor = 0)
        elif self.func == 'bbands':
            up,ma,low = ta.BBANDS(kl['c'], **self.params)
            self.data[self.col[0]] = up
            self.data[self.col[1]] = ma
            self.data[self.col[2]] = low
        elif self.func == 'macd':
            dif,dea,macd = ta.MACD(kl['c'], **self.params) #12 26 9 / 6 12 9
            self.data[self.col[0]] = dif
            self.data[self.col[1]] = dea
            self.data[self.col[2]] = macd
        elif self.func == 'stoch':
            slowk,slowd = ta.STOCH(kl['h'],kl['l'],kl['c'], **self.params)
            self.data[self.col[0]] = slowk
            self.data[self.col[1]] = slowd
        elif self.func == 'stochrsi':
            fastk,fastd = ta.STOCHRSI(kl['c'], **self.params)
            self.data[self.col[0]] = fastk
            self.data[self.col[1]] = fastd
        else:
            log.err("haven't implement func:%s"%(self.func))

    def graphic(self):
        while self.data.empty == True:
            log.dbg("graphic waiting data!")
            time.sleep(1)
        df = pd.DataFrame()
        if self.func == 'macd':
            df['zero'] = pd.Series([0]*self.kl['c'].size)
            df['price'] = pd.Series(self.kl['c'] - self.kl['c'].mean()) #price fixed around 0 for trend analyse
        else:
            df['price'] = self.kl['c']
        df = pd.concat([df, self.data], axis=1)
        #print(df)
        _graphic(df, self.func)

kama = TechnicalAnalysis('kama', ['kama'], timeperiod=10)
sma_fast = TechnicalAnalysis('sma', ['fast'], timeperiod=5)
sma_slow = TechnicalAnalysis('sma', ['slow'], timeperiod=10)
bbands = TechnicalAnalysis('bbands', ['up','mid', 'low'], timeperiod = 10, nbdevup = 1.5, nbdevdn = 1.5, matype = 0)
macd = TechnicalAnalysis('macd', ['dif','dea', 'macd'], fastperiod = 12, slowperiod = 26, signalperiod = 9)
stoch = TechnicalAnalysis('stoch', ['slowk', 'slowd'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
stochrsi = TechnicalAnalysis('stochrsi', ['fastk', 'fastd'], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)


def bbands_signal(timestamp, price):
    signal = 0
    if timestamp > 0:
        row = bbands.get_data_timestamp(timestamp)
        up,low = row['up'],row['low']
        ma_fast = sma_fast.get_data_timestamp(timestamp)
        ma_fast = row['fast']
        ma_slow = sma_slow.get_data_timestamp(timestamp)
        ma_slow = row['slow']
    else:
        row = bbands.get_last_data()
        up,low = row['up'],row['low']
        row = sma_fast.get_last_data()
        ma_fast = row['fast']
        row = sma_slow.get_last_data()
        ma_slow = row['slow']

    if isclose(ma_fast, ma_slow): #Shock market
        if price < low:
            signal = 1
        elif price > up:
            signal = -1
    else:
        if price < low:
            signal = -1
        elif price > up:
            signal = 1


if __name__ == '__main__':
    #bbands.graphic()
    #macd.graphic()
    #stoch.graphic()
    stochrsi.graphic()
    #kama.graphic()
    #up,low = bbands.get_band_timestamp(1533968011)
    #print(up, low)

    #df = df_merge(sma_fast.get_data(), sma_slow.get_data()) ##.rename(columns={'real':'fast'})
    #_graphic(df, 'mixed')
    mkt.stop()

    
