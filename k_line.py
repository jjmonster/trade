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


class kline:
    def __init__(self):
        self.fwk = frmwk()
        self.reg = region()

    def gather_data(self, pair):
        self.ochl = self.fwk.get_K_line(pair, limit=10, dtype="1day") #t o c h l v a
        self.amount = [i.pop() for i in self.ochl]
        self.volume = [i.pop() for i in self.ochl]
        min_x = 9999999
        max_x = 0
        for i in self.ochl:
            i[0] = mdates.epoch2num(i[0]) #convert timestamp to matplotlib.dates num format
            min_x = min(i[0], min_x)
            max_x = max(i[0], max_x)

        r_c = self.reg.get_reg_count()
        r = self.reg.get()
        self.r_lines = []
        for i in range(r_c):
            self.r_lines.append([[min_x, max_x],[r[i]['l'],r[i]['l']]])
            self.r_lines.append([[min_x, max_x],[r[i]['h'],r[i]['h']]])

    def graphic(self):
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111) # only one plot
        candlestick_ochl(self.ax1, self.ochl, width=0.4, colorup='#77d879', colordown='#db3f3f')
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax1.xaxis.set_major_locator(mdates.DayLocator())
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
        plt.show()

if __name__ == '__main__':
    config.load_cfg_all()
    pair = config.get_cfg("coin1")+config.get_cfg("coin2")
    
    kl = kline()
    kl.reg.start()
    kl.gather_data(pair)
    kl.graphic()
    kl.reg.stop()