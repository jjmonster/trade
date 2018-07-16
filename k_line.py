import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
from framework import frmwk
import config


class kline:
    def __init__(self):
        self.fwk = frmwk()

    def gather_data(self, pair):
        self.ohlc = self.fwk.get_K_line(pair)
        print(self.ohlc)
        

    def graph(self, pair):
        self.gather_data(pair)
        plt.figure()
        ax1 = plt.subplot2grid((1,1), (0,0)) # only one grid
        candlestick_ohlc(ax1, self.ohlc, width=0.4, colorup='#77d879', colordown='#db3f3f')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.show()


if __name__ == '__main__':
    config.load_cfg_all()
    pair = config.get_cfg("coin1")+config.get_cfg("coin2")
    kl = kline()
    kl.graph(pair)