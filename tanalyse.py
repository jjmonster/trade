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

def get_df_data_last(df):
    while df.empty == True:
        log.info("get_df_data_last waiting data!")
        time.sleep(1)
    return df.iloc[-1] #or irow(-1)?

def get_df_index_timestamp(df, timestamp):
    while df.empty == True:
        log.info("get_df_data_timestamp waiting data!")
        time.sleep(1)
    if timestamp <= 0:
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

def get_df_data_timestamp(df, timestamp):
    return df.iloc[get_df_index_timestamp(timestamp)]

def cut_df_data_timestamp(df, timestamp):
    return df.iloc[0:get_df_index_timestamp(timestamp), :]
    

def _graphic(df, title):
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
        ax1.plot(t, column, lcs)

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
        self.sig = ''
        self.form = ''
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
            self.data['slowk'] = self.data['slowk']/10
            self.data['slowd'] = self.data['slowd']/10
            df['up'] = pd.Series([8]*self.kl['c'].size)
            df['low'] = pd.Series([2]*self.kl['c'].size)
            df['price'] = self.kl['c']
        elif self.func == 'stochrsi':
            self.data['fastk'] = self.data['fastk']/10
            self.data['fastd'] = self.data['fastd']/10
            df['up'] = pd.Series([8]*self.kl['c'].size)
            df['low'] = pd.Series([2]*self.kl['c'].size)
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
        row = self.get_data_timestamp(timestamp)
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

    def ta_signal(self, timestamp, price):
        self.ta_form(timestamp, price)
        if self.form == 'up' or self.form == 'upper':
            self.sig = 'sell'
        elif self.form == 'low' or self.form == 'lower':
            self.sig = 'buy'
        else:
            self.sig = ''

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
        pass
    def ta_signal(self, timestamp, price):
        pass

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

kama = Kama(timeperiod=10)
sma_fast = Sma('fast', timeperiod=5)
sma_slow = Sma('slow', timeperiod=10)
bbands = Bbands(timeperiod = 10, nbdevup = 1.5, nbdevdn = 1.5, matype = 0)
macd = Macd(fastperiod = 12, slowperiod = 26, signalperiod = 9)
stoch = Stoch(fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
stochrsi = Stochrsi(timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)

if __name__ == '__main__':
    #sma_fast.graphic()
    #sma_slow.graphic()
    #kama.graphic()
    #bbands.graphic()
    #macd.graphic()
    #stoch.graphic()
    #stochrsi.graphic()
    
    #up,low = bbands.get_band_timestamp(1533968011)
    #print(up, low)

    #df = df_merge(sma_fast.get_data(), sma_slow.get_data(), bbands.get_data(), macd.get_data()) ##.rename(columns={'real':'fast'})
    #_graphic(df, 'mixed')
    mkt.stop()

    
