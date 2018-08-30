#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logger import log
from utils import isclose
from market import mkt
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
    def __init__(self):
        self.data = pd.DataFrame()
        self.kl = pd.DataFrame()
        self.sig = ''
        self.form = ''

    def _wait_data(self):
        while self.kl.empty == True or self.data.empty == True:
            log.info("waiting data!")
            time.sleep(1)

    def get_kl(self):
        self._wait_data()
        return self.kl

    def get_data(self):
        self._wait_data()
        return self.data

    def get_data_timestamp(self, timestamp):
        self._wait_data()
        return _get_df_data_timestamp(self.data, timestamp)

    def get_row_data_last(self):
        self._wait_data()
        return _get_row_data_last(self.data)

    def get_row_data_timestamp(self,timestamp):
        self._wait_data()
        return _get_row_data_timestamp(self.data, timestamp)

    def graphic(self, title):
        self._wait_data()
        _graphic(self.data, title)


class Bbands(TechnicalAnalysis):
    def __init__(self, **params):
        super(Bbands, self).__init__()
        self.params = dict({'timeperiod':20, 'nbdevup':1.5, 'nbdevdn':1.5, 'matype':0}, **params)

    def start(self):
        mkt.register_handle('kline', self.handle_data)

    def stop(self):
        mkt.unregister_handle('kline', self.handle_data)

    def handle_data(self, kl):
        self.kl = kl #.copy()
        self.data['t'] = kl['t']
        self.data['up'],self.data['mid'],self.data['low'] = ta.BBANDS(kl['c'], **self.params)

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
        super(Macd, self).__init__()
        self.params = dict({'fastperiod':12, 'slowperiod':26, 'signalperiod':9}, **params)

    def start(self):
        mkt.register_handle('kline', self.handle_data)

    def stop(self):
        mkt.unregister_handle('kline', self.handle_data)

    def handle_data(self, kl):
        self.kl = kl #.copy()
        self.data['t'] = kl['t']
        self.data['dif'],self.data['dea'],self.data['macd'] = ta.MACD(kl['c'], **self.params) #12 26 9 / 6 12 9
        self.data['zero'] = pd.Series([0]*kl['c'].size)
        #self.data['price'] = pd.Series(kl['c'] - kl['c'].mean()) #price fixed around 0 for trend analyse


    def ta_form(self, timestamp, price):
        self.form = ''
        df = self.get_data_timestamp(timestamp)
        if df.index.size < 3:
            return
        macd = df['macd']
        m1,m2,m3 = macd.iloc[-3], macd.iloc[-2], macd.iloc[-1]
        if m1 < m2:
            if m2 < m3:     #||| #'rising'
                self.form = 'f1'
            elif m2 > m3:   #1|1
                self.form = 'f2'
        elif m1 > m2:
            if m2 > m3:    #||| #'falling'
                self.form = 'f3' 
            elif m2 < m3:  #|1|
                self.form = 'f4'

        if self.form == 'f1' and m1 < macd.min()/3:
            self.form = 'rising'
        elif self.form == 'f3' and m1 > macd.max()/3:
            self.form = 'falling'

        if self.form != 'rising' and self.form != 'falling':
            if m1 < 0 and m2 > 0 and m3 > m2: #crossing up
                self.form = 'rising'
            elif m1 > 0 and m2 < 0 and m3 < m2: #crossing down
                self.form = 'falling'

        return self.form

    def ta_signal(self, timestamp, price):
        self.ta_form(timestamp, price)
        if self.form == 'rising':
            self.sig = 'buy'
        elif self.form == 'falling':
            self.sig = 'sell'
        else:
            self.sig = 'standby'
        return self.sig


class Stoch(TechnicalAnalysis):
    def __init__(self, **params):
        super(Stoch, self).__init__()
        self.params = dict({'fastk_period':9, 'slowk_period':3, 'slowk_matype':0, 'slowd_period':3, 'slowd_matype':0}, **params)

    def start(self):
        mkt.register_handle('kline', self.handle_data)

    def stop(self):
        mkt.unregister_handle('kline', self.handle_data)

    def handle_data(self, kl):
        self.kl = kl #.copy()
        self.data['t'] = kl['t']
        self.data['slowk'],self.data['slowd'] = ta.STOCH(kl['h'],kl['l'],kl['c'], **self.params)
        self.data['up'] = pd.Series([80]*kl['c'].size)
        self.data['low'] = pd.Series([20]*kl['c'].size)
        self.data['mid'] = pd.Series([50]*kl['c'].size)
        self.data['dif'] = (self.data['slowk'] - self.data['slowd']) + 50

    def ta_form(self, timestamp, price):
        row = self.get_row_data_timestamp(timestamp)
        slowk,slowd = row['slowk'], row['slowd']
        if slowd > 80:
            self.form = 'overbuy'
        elif slowd < 20:
            self.form = 'oversell'
        else:
            self.form = ''
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
        super(Stochrsi, self).__init__()
        self.params = dict({'timeperiod':14, 'fastk_period':5, 'fastd_period':3, 'fastd_matype':0}, **params)

    def start(self):
        mkt.register_handle('kline', self.handle_data)

    def stop(self):
        mkt.unregister_handle('kline', self.handle_data)

    def handle_data(self, kl):
        self.kl = kl #.copy()
        self.data['t'] = kl['t']
        self.data['fastk'],self.data['fastd'] = ta.STOCHRSI(kl['c'], **self.params)
        self.data['up'] = pd.Series([80]*kl['c'].size)
        self.data['low'] = pd.Series([20]*kl['c'].size)
        self.data['mid'] = pd.Series([50]*kl['c'].size)

    def ta_form(self, timestamp, price):
        pass
    def ta_signal(self, timestamp, price):
        pass

class Ma(TechnicalAnalysis):
    def __init__(self, indicator,   col_name, **params):
        super(Ma, self).__init__()
        self.indicator = indicator

    def start(self):
        mkt.register_handle('kline', self.handle_data)

    def stop(self):
        mkt.unregister_handle('kline', self.handle_data)

    def handle_data(self, kl):
        self.kl = kl #.copy()
        self.data['t'] = kl['t']
        if self.indicator == 'ma':
            #MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
            self.data[col_name] = ta.MA(kl['c'], **self.params)
        elif self.indicator == 'wma':
            self.data[col_name] = ta.WMA(kl['c'], **self.params)
        elif self.indicator == 'sma':
            self.data[col_name] = ta.SMA(kl['c'], **self.params)
        elif self.indicator == 'ema':
            self.data[col_name] = ta.EMA(kl['c'], **self.params)
        elif self.indicator == 'dema':
            self.data[col_name] = ta.DEMA(kl['c'], **self.params)
        elif self.indicator == 'trima':
            self.data[col_name] = ta.TRIMA(kl['c'], **self.params)
        elif self.indicator == 'kama':
            self.data[col_name] = ta.KAMA(kl['c'], **self.params)
        elif self.indicator == 't3':
            self.data[col_name] = ta.T3(kl['c'], **self.params)##, vfactor = 0)

    def ta_form(self, timestamp, price):
        pass
    def ta_signal(self, timestamp, price):
        pass


class Atr(TechnicalAnalysis):
    def __init__(self, **params):
        super(Atr, self).__init__()
        self.params = dict({'timeperiod':14}, **params)
        
    def start(self):
        mkt.register_handle('kline', self.handle_data)

    def stop(self):
        mkt.unregister_handle('kline', self.handle_data)

    def handle_data(self, kl):
        self.kl = kl #.copy()
        self.data['t'] = kl['t']
        self.data['real'] = ta.ATR(kl['h'], kl['l'], kl['c'], **self.params)

    def ta_form(self, timestamp, price):
        #row = self.get_row_data_timestamp(timestamp)
        #atr = row['real']
        return self.form

    def ta_signal(self, timestamp, price):
        return self.sig
    
if __name__ == '__main__':
    atr = Atr()
    #bbands = Bbands()
    #macd = Macd()
    #stoch = Stoch()
    #stochrsi = Stochrsi()
    #kama = Ma('kama', 'kama', timeperiod=10)
    #sma_fast = Ma('sma', 'fast', timeperiod=5)
    #sma_slow = Ma('sma', 'slow', timeperiod=20)
    #sma_fast.graphic()
    #sma_slow.graphic()
    #kama.graphic()
    atr.graphic('atr')
    #bbands.graphic()
    #macd.graphic()
    #stoch.graphic()
    #stochrsi.graphic()
    
    #up,low = bbands.get_band_timestamp(1533968011)
    #print(up, low)

    #df = df_merge(sma_fast.get_data(), sma_slow.get_data(), bbands.get_data(), macd.get_data()) ##.rename(columns={'real':'fast'})
    #_graphic(df, 'mixed')


    
