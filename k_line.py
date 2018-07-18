import matplotlib.pyplot as plt
#import mpl_finance
from mpl_finance import candlestick_ochl,index_bar
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import numpy as np

from region import region
from framework import frmwk
import config
import threading
import time


class kline:
    def __init__(self):
        self.fwk = frmwk()
        self.reg = region()
        
        plt.ion()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111) # only one plot


    def update_k_line(self, tochlva):
        self.amount = [i.pop() for i in tochlva]
        self.volume = [i.pop() for i in tochlva]
        self.k_lines,self.k_patches = candlestick_ochl(self.ax1, tochlva, width=0.4, colorup='#77d879', colordown='#db3f3f')
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax1.xaxis.set_major_locator(mdates.DayLocator())
        self.x = []
        for i in tochlva:
            i[0] = mdates.epoch2num(i[0]) #convert timestamp to matplotlib.dates num format
            self.x.append(i[0])
       self.x0 = min(self.x)
       self.x1 = max(self.x)
        

    def update_p_line(self, price):
        if 'self.p_line' in locals().keys() and isinstance(self.p_line, matplotlib.lines):
            self.p_line.set_xdata([self.x0,self.x1])
            self.p_line.set_ydata([price,price])
        else:
            self.p_line = Line2D([self.x0, self.x1],[price, price], color='g')
            self.ax1.add_line(self.p_line)

    def update_r_line(self, region):
        r_c = self.reg.get_reg_count()
        if 'self.r_lines' not in locals().keys():
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

    def gather_data(self, pair):
        #self.ochl = self.fwk.get_K_line(pair, limit=10, dtype="1day") #t o c h l v a
        self.amount = [i.pop() for i in self.ochl]
        self.volume = [i.pop() for i in self.ochl]

        
        r = self.reg.get()
        self.r_lines = []
        for i in range(r_c):
            self.r_lines.append([[min_x, max_x],[r[i]['l'],r[i]['l']]])
            self.r_lines.append([[min_x, max_x],[r[i]['h'],r[i]['h']]])

    def update(self):
        lines = self.ax1.get_lines()
        lines.pop().remove()
        
        plt.pause(10)

        
    def graphic(self):
        
        #self.ax1.grid(True)
        #line1 = Line2D(xdata=[736883.0,736892.0],ydata=[0.0919,0.0919], color="r")
        #self.ax1.add_line(line1)
        plt.xticks(rotation=45)
        for i in self.r_lines:
            l = Line2D(xdata = i[0], ydata = i[1])
            self.ax1.add_line(l)
        lines = self.ax1.get_lines()
        for i in lines:
            print(i.get_data())
        self.update()
        plt.draw()

if __name__ == '__main__':
    config.load_cfg_all()
    pair = config.get_cfg("coin1")+config.get_cfg("coin2")
    
    kl = kline()
    kl.reg.start()
    kl.gather_data(pair)
    kl.graphic()
    for i  in range(10):
        kl.update()
    kl.reg.stop()
