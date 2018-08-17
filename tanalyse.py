#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import cfg
from framework import fwk
from market import mkt
from logger import log
from utils import isclose
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime,timedelta
import pandas as pd
import numpy as np
import talib as ta
import time


def _get_df_index_timestamp(df, timestamp):
    if timestamp <= 0:     ######return last if timestamp <= 0
        return df.index.size - 1
    t = df['t']
    if timestamp < t[0]:
        log.war("warning! timestamp=%d less than %d"%(timestamp, t[0]))
        return 0
    idx = -1
    for i in range(t.size):
        if timestamp >= t[i]:
            idx += 1
        else:
            break
    return idx

def _get_df_data_timestamp(df, timestamp):
    return df.iloc[0:_get_df_index_timestamp(df,timestamp), :]

def _get_row_data_last(df):
    return df.iloc[-1] #or irow(-1)?

def _get_row_data_timestamp(df, timestamp):
    return df.iloc[_get_df_index_timestamp(df,timestamp)]


def _graphic(df, title):
    if title != 'bbands':
        fig, axes = plt.subplots(2,1,sharex=True, figsize=(12,8))
        ax1,ax2= axes[0],axes[1]
    else:
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
    line_color = ('b','g','r','c','m','y','k')#,'w')
    line_maker = ('.',',','o') ###...
    line_style = ('-', '--', '-.', ':')

    t = list(map(datetime.fromtimestamp, df['t']))
    for i in range(df.columns.size): #exclude 't'
        if df.columns[i] == 't':
            continue
        column = df[df.columns[i]]
        lcs = line_color[int(i%len(line_color))]+line_style[int(i/len(line_color))]
        if title == 'bbands':
            ax1.plot(t, column, lcs)
        else:
            if df.columns[i] == 'price':
                ax1.plot(t, column, lcs)
            else:
                ax2.plot(t, column, lcs)

    ax1.set_title(title, fontproperties="SimHei")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
    ax1.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

def _df_merge(*df):
    data = df[0]
    if len(df) > 1:
        for i in range(len(df)-1):
            data = pd.merge(data, df[i+1], how='left', on='t')
    return data

def _coordinate_repeat(x, y): ##polygonal line
    arr1 = list(np.array(x).repeat(2))
    arr2 = list(np.array(y).repeat(2))
    arr1.pop(0)
    arr2.pop(-1)
    return pd.Series(arr1), pd.Series(arr2)


class  TechnicalAnalysis():
    def __init__(self, func, columns, **params):
        self.data = pd.DataFrame()
        self.kl = pd.DataFrame()
        self.func = func
        self.col = columns
        self.params = params
        self.sig = ''
        self.form = ''
        mkt.register_handle('kline', self.handle_data)

    def get_kl(self):
        while self.kl.empty == True:
            log.info("waiting data!")
            time.sleep(1)
        return self.kl

    def get_data(self):
        while self.data.empty == True:
            log.info("waiting data!")
            time.sleep(1)
        return self.data

    def get_data_timestamp(self, timestamp):
        while self.data.empty == True:
            log.info("waiting data!")
            time.sleep(1)
        return _get_df_data_timestamp(self.data, timestamp)

    def get_row_data_last(self):
        while self.data.empty == True:
            log.info("waiting data!")
            time.sleep(1)
        return _get_row_data_last(self.data)

    def get_row_data_timestamp(self,timestamp):
        while self.data.empty == True:
            log.info("waiting data!")
            time.sleep(1)
        return _get_row_data_timestamp(self.data, timestamp)

    def handle_data(self, kl):
        if kl.empty == True:
            return
        self.kl = kl.copy()
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
            up,mid,low = ta.BBANDS(kl['c'], **self.params)
            self.data[self.col[0]] = up
            self.data[self.col[1]] = mid
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
        elif self.func == 'stoch':
            #df['price'] = pd.Series(self.kl['c']*(50/self.kl['c'].mean())) #price fixed around 50 for trend analyse
            df['up'] = pd.Series([80]*self.kl['c'].size)
            df['low'] = pd.Series([20]*self.kl['c'].size)
            df['mid'] = pd.Series([50]*self.kl['c'].size)
            df['price'] = self.kl['c']
            df['dif'] = (self.data['slowk'] - self.data['slowd']) + 50
        elif self.func == 'stochrsi':
            df['up'] = pd.Series([80]*self.kl['c'].size)
            df['low'] = pd.Series([20]*self.kl['c'].size)
            df['mid'] = pd.Series([50]*self.kl['c'].size)
            df['price'] = self.kl['c']
        else:
            df['price'] = self.kl['c']
        df = pd.concat([df, self.data], axis=1)
        #print(df)
        _graphic(df, self.func)


class Bbands(TechnicalAnalysis):
    def __init__(self, **params):
        super(Bbands, self).__init__('bbands', ['up','mid', 'low'], **params)

    def ta_form(self, timestamp, price):
        row = self.get_row_data_timestamp(timestamp)
        up,mid,low = row['up'],row['mid'],row['low']
        if isclose(up, low):
            self.form = 'up_low_close'
        elif isclose(up, price):
            self.form = 'up'
        elif isclose(low, price):
            self.form = 'low'
        elif isclose(mid, price):
            self.form = 'mid'
        elif price > up:
            self.form = 'upper'
        elif price < low:
            self.form = 'lower'
        else:
            if price > mid:
                self.form = 'midup'
            elif price < mid:
                self.form = 'midlow'
        return self.form

    def ta_signal(self, timestamp, price):
        self.ta_form(timestamp, price)
        if self.form == 'up' or self.form == 'upper':
            self.sig = 'sell'
        elif self.form == 'low' or self.form == 'lower':
            self.sig = 'buy'
        else:
            self.sig = 'standby'
        return self.sig

class Macd(TechnicalAnalysis):
    def __init__(self, **params):
        super(Macd, self).__init__('macd', ['dif','dea', 'macd'], **params)

    def ta_form(self, timestamp, price):
        pass
    def ta_signal(self, timestamp, price):
        pass

class Stoch(TechnicalAnalysis):
    def __init__(self, **params):
        super(Stoch, self).__init__('stoch', ['slowk', 'slowd'], **params)

    def ta_form(self, timestamp, price):
        row = self.get_row_data_timestamp(timestamp)
        slowk,slowd = row['slowk'], row['slowd']
        if slowd > 80:
            self.form = 'overbuy'
        elif slowd < 20:
            self.form = 'oversell'
        else:
            self.form = None
            df = self.get_data_timestamp(timestamp)
            if df.index.size < 3:
                return
            dif = df['slowk'] - df['slowd']
            if isclose(dif.iloc[-1], 0):
                self.form = 'crossing' ### need forecast next form?
            if dif.iloc[-1] > 0: #check if crossed up
                if dif.iloc[-2] < 0 or isclose(dif.iloc[-2], 0):
                    self.form = 'crossup'
                else:
                    self.form = 'up' ##continus up
            elif dif.iloc[-1] < 0: #check if crossed down
                if dif.iloc[-2] > 0 or isclose(dif.iloc[-2], 0):
                    self.form = 'crossdown'
                else:
                    self.form = 'down'  ##continus down
        return self.form
        
    def ta_signal(self, timestamp, price):
        self.ta_form(timestamp, price)
        if self.form == 'oversell' or self.form == 'crossup':
            self.sig = 'buy'
        elif self.form == 'overbuy' or self.form == 'crossdown':
            self.sig = 'sell'
        else:
            self.sig = 'standby'
        return self.sig

class Stochrsi(TechnicalAnalysis):
    def __init__(self, **params):
        super(Stochrsi, self).__init__('stochrsi', ['fastk', 'fastd'], **params)

    def ta_form(self, timestamp, price):
        pass
    def ta_signal(self, timestamp, price):
        pass


class Kama(TechnicalAnalysis):
    def __init__(self, **params):
        super(Kama, self).__init__('kama', ['kama'], **params)

    def ta_form(self, timestamp, price):
        pass
    def ta_signal(self, timestamp, price):
        pass


class Sma(TechnicalAnalysis):
    def __init__(self,   col_name, **params):
        super(Sma, self).__init__('sma', [col_name], **params)

    def ta_form(self, timestamp, price):
        pass
    def ta_signal(self, timestamp, price):
        pass

#kama = Kama(timeperiod=10)
#sma_fast = Sma('fast', timeperiod=5)
#sma_slow = Sma('slow', timeperiod=20)
bbands = Bbands(timeperiod = 20, nbdevup = 1.5, nbdevdn = 1.5, matype = 0)
macd = Macd(fastperiod = 12, slowperiod = 26, signalperiod = 9)
stoch = Stoch(fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
#stochrsi = Stochrsi(timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)

if __name__ == '__main__':
    #sma_fast.graphic()
    #sma_slow.graphic()
    #kama.graphic()
    #bbands.graphic()
    #macd.graphic()
    stoch.graphic()
    #stochrsi.graphic()
    
    #up,low = bbands.get_band_timestamp(1533968011)
    #print(up, low)

    #df = df_merge(sma_fast.get_data(), sma_slow.get_data(), bbands.get_data(), macd.get_data()) ##.rename(columns={'real':'fast'})
    #_graphic(df, 'mixed')
    mkt.stop()

    
