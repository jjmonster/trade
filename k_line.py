import matplotlib.pyplot as plt
#import mpl_finance
from mpl_finance import candlestick_ochl
from datetime import datetime
import matplotlib.dates as mdates

from framework import frmwk
import config


class kline:
    def __init__(self):
        self.fwk = frmwk()

    def gather_data(self, pair):
        self.ochl = self.fwk.get_K_line(pair, limit=10, dtype="1day") #t o c h l v a
        self.amount = [i.pop() for i in self.ochl]
        self.volume = [i.pop() for i in self.ochl]
        #self.date = [i.pop(0) for i in self.ochl]
        #date = [datetime.fromtimestamp(i[0]) for i in self.ochl]
        #print(date)
        print(self.ochl)
        

    def graph(self, pair):
        self.gather_data(pair)
        plt.figure()
        ax1 = plt.subplot2grid((1,1), (0,0)) # only one grid        
        candlestick_ochl(ax1, self.ochl) # width=0.8, colorup='#77d879', colordown='#db3f3f')
        #ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator())
        ax1.xaxis_date()
        ax1.grid(True)
        plt.xticks(rotation=30)
        #plt.xlabel('Date')
        #plt.ylabel('Price')
        plt.show()


if __name__ == '__main__':
    config.load_cfg_all()
    pair = config.get_cfg("coin1")+config.get_cfg("coin2")
    kl = kline()
    kl.graph(pair)