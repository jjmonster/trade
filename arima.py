#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import cfg
from framework import fwk
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
from statsmodels.tsa.arima_model import ARIMA
import matplotlib.dates as mdates
from datetime import datetime,timedelta

class arima():
    def __init__(self):
        self.day_history = 15
        self.dtype = "1hour"
        return

    def get_kline(self):
        pair = cfg.get_cfg("coin1")+cfg.get_cfg("coin2")
        limit = 1000
        if self.dtype == "1day":
            limit = min(limit, self.day_history)
        elif self.dtype == "6hour":
            limit = min(limit, self.day_history*4)
        elif self.dtype == "1hour":
            limit = min(limit, self.day_history*24)
        elif self.dtype == "1min":
            limit = min(limit, self.day_history*24*60)
        else:
            limit = 10

        kl = fwk.get_kline(pair, limit, self.dtype)
        return kl

    def get_date(self, *kl):
        if len(kl) == 0:
            kl = self.get_kline()
        else:
            kl = kl[0]
        #date = [mdates.epoch2num(i[0]) for i in kl]
        date = [datetime.fromtimestamp(i[0]) for i in kl]
        return date

    def get_close_price(self, *kl):
        if len(kl) == 0:
            kl = self.get_kline()
        else:
            kl = kl[0]
        cp = [i[1] for i in kl]
        #print("get_close_price", cp)
        return cp

    def orig_data_graphic(self):
        kl = self.get_kline()
        cp = self.get_close_price(kl)
        date = self.get_date(kl)
        dta = pd.Series(cp, index=date)
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
        dta.plot(ax=ax1)
        plt.show()
        
    def diff_data_graphic(self):
        kl = self.get_kline()
        cp = self.get_close_price(kl)
        date = self.get_date(kl)
        dta = pd.Series(cp, index=date)
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(211)
        ax1.set_title("diff 1")
        diff1 = dta.diff(1)
        diff1.plot(ax=ax1)
        ax2= fig.add_subplot(212)
        ax2.set_title("diff 2")
        diff2 = dta.diff(2)
        diff2.plot(ax=ax2)
        plt.show()

    def acf_pacf(self):
        kl = self.get_kline()
        cp = self.get_close_price(kl)
        date = self.get_date(kl)
        dta = pd.Series(cp, index=date)
        diff1 = dta.diff(1)
        fig = plt.figure(figsize=(12,8))
        ax1=fig.add_subplot(211)
        fig = sm.graphics.tsa.plot_acf(dta,lags=40,ax=ax1)
        ax2 = fig.add_subplot(212)
        fig = sm.graphics.tsa.plot_pacf(dta,lags=40,ax=ax2)
        plt.show()
        
    def arima(self):
        kl = self.get_kline()
        cp = self.get_close_price(kl)
        date = self.get_date(kl)
        #t = datetime.fromtimestamp(date[-1].timestamp()+24*60*60)
        t = date[-1] + timedelta(days=int(self.day_history/5)) #days seconds ...
        print("predict date:", date[-1],"--->", t)

        dta = pd.Series(cp, index=date)
        print(dta)
        model=ARIMA(dta,order=(4,1,3)) #P D Q
        result=model.fit()
        pred=result.predict( date[-10], t,dynamic=True,typ='levels')
        plt.figure(figsize=(12,8))
        plt.plot(dta, 'ro-')
        plt.xticks(rotation=45)
        plt.plot(pred, 'go-')

        plt.show()



if __name__ == '__main__':
    a = arima()
    #a.diff_data_graphic()
    a.acf_pacf()
    a.arima()
    
