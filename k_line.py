#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
#import mpl_finance
from mpl_finance import candlestick_ochl,candlestick2_ochl,index_bar
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import numpy as np

from region import reg
from market import mkt
from config import cfg


class kline:
    def __init__(self):
        self.p_line = None
        self.r_lines = None
        self.k_lines = None
        self.k_patches = None
        plt.ion()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111) # only one plot

    def update_k_line(self, tochlva):
        print("update_k_line", tochlva)
        self.amount = [i.pop() for i in tochlva]
        self.volume = [i.pop() for i in tochlva]        
        self.x = []
        for i in tochlva:
            i[0] = mdates.epoch2num(i[0]) #convert timestamp to matplotlib.dates num format
            self.x.append(i[0])
        self.x0 = min(self.x)
        self.x1 = max(self.x)
        if self.k_lines == None and self.k_patches == None:
            self.k_lines,self.k_patches = candlestick_ochl(self.ax1, tochlva)#, width=0.4, colorup='#77d879', colordown='#db3f3f')
        else:
            self.k_lines,self.k_patches = candlestick_ochl(self.ax1, tochlva)
            
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax1.xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45)
#        plt.draw()
#        plt.pause(0.001)

    def update_p_line(self, price):
        #print("update_p_line", price)
        if self.k_lines == None: #make sure draw kline first
            return
        if self.p_line != None:
            self.p_line.set_xdata([self.x0,self.x1])
            self.p_line.set_ydata([price,price])
        else:
            self.p_line = Line2D([self.x0, self.x1],[price, price], color='g')
            self.ax1.add_line(self.p_line)
        lines = self.ax1.get_lines()
        #for i in lines:
        #    print("222...", i.get_data())
 #       plt.draw()
 #       plt.pause(0.001)
        
    def update_r_line(self, region):
        print("update_r_line", region)
        r_c = reg.get_reg_count()
        if self.r_lines == None:
            self.r_lines = []
            for i in range(r_c):
                l = Line2D([self.x0, self.x1], [region[i]['l'], region[i]['l']])
                self.ax1.add_line(l)
                self.r_lines.append(l)
                h = Line2D([self.x0, self.x1], [region[i]['h'], region[i]['h']])
                self.ax1.add_line(h)
                self.r_lines.append(h)
        elif r_c == len(self.r_lines)*2:
            for i in range(r_c):
                self.r_lines[i*2].set_xdata([self.x0, self.x1])
                self.r_lines[i*2].set_ydata([region[i]['h'], region[i]['h']])
                self.r_lines[i*2+1].set_xdata([self.x0, self.x1])
                self.r_lines[i*2+1].set_ydata([region[i]['h'], region[i]['h']])
#        plt.draw()
#        plt.pause(0.001)

if __name__ == '__main__':
    kl = kline()
#    data = [[1531180800, 0.0814, 0.081, 0.0905, 0.0723, 103771393.83420932, 8323556.042502045], [1531267200, 0.081049, 0.087, 0.08888, 0.0775, 1017550622.0969594, 83442865.2505877], [1531353600, 0.087099, 0.082961, 0.0878, 0.08112, 1159967596.6858056, 96682491.57647811], [1531440000, 0.082961, 0.0864, 0.0881, 0.0801, 1257620327.308484, 107429085.54205538], [1531526400, 0.086572, 0.107208, 0.109, 0.0854, 1062604752.9157971, 103724241.52636482], [1531612800, 0.107207, 0.1013, 0.125, 0.100481, 436595503.8351548, 47782891.340352535], [1531699200, 0.1013, 0.105216, 0.112027, 0.0981, 248884940.52353838, 26425104.860884394], [1531785600, 0.105216, 0.118753, 0.12, 0.105187, 245871414.94902983, 27615576.86779892], [1531872000, 0.118668, 0.115272, 0.121222, 0.113, 205562493.2313652, 24293006.69561948], [1531958400, 0.115271, 0.114523, 0.11669, 0.113432, 48454220.13353385, 5556155.479947055]]
#    kl.update_k_line(data)
#    kl.update_p_line(0.0914)
#    kl.update_p_line(0.1014)
#    kl.update_k_line(data)

    mkt.handle_register('kline', kl.update_k_line)
    mkt.handle_register('price', kl.update_p_line)

    mkt.start()
    #kl.reg.start()
    #kl.reg.stop()
    time.sleep(10)
    #plt.pause(10)
    mkt.stop()
