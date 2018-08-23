#!/usr/bin/python
# -*- coding: UTF-8 -*-

#from tkinter import *
import tkinter as tk
from tkinter import ttk,scrolledtext
from collections import OrderedDict

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
#from matplotlib.figure import Figure

from mpl_finance import candlestick_ochl,candlestick2_ochl
from datetime import datetime,timedelta
import numpy as np
import pandas as pd

from config import cfg
from market import mkt
from signalslot import sslot
from tanalyse import Bbands,Macd,Stoch
from robot import Robot


def ta_graphic(indicator, ax, *params):
    df = params[0]
    if indicator == 'kline':
        candlestick_ochl(ax, np.array(df))#, width=0.4, colorup='#77d879', colordown='#db3f3f')
    else:
        line_color = ('b','g','r','c','m','y','k')#,'w')
        line_maker = ('.',',','o') ###...
        line_style = ('-', '--', '-.', ':')
        t = list(map(datetime.fromtimestamp, df['t']))
        for i in range(df.columns.size): #exclude 't'
            if df.columns[i] == 't':
                continue
            col = df[df.columns[i]]
            cms = line_color[int(i%len(line_color))]+line_style[int(i/len(line_color))]
            ax.plot(t, col, cms)

    ax.set_title(indicator, fontproperties="SimHei")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
    ax.legend()
    plt.xticks(rotation=45)
    #plt.show()

    if len(params) > 1:
        hist = params[1]
        if len(hist) > 0:
            for i in range(len(hist)):
                time = datetime.fromtimestamp(hist[i][0])
                type = hist[i][1]
                price = hist[i][2]
                if type == 'open_buy':
                    cms = 'r+'
                elif type == 'margin_buy' or type == 'loss_buy':
                    cms = 'rx'
                elif type == 'open_sell':
                    cms = 'g+'
                elif type == 'margin_sell' or type == 'loss_sell':
                    cms = 'gx'
                ax.plot([time], [price], cms)

class windows:
    def __init__(self):
        pass

    def mainloop(self):
        self.win = tk.Tk()
        #bind exit method
        self.win.protocol("WM_DELETE_WINDOW", self.exit)
        self.win.bind('<Escape>', lambda e: self.exit())

        #self.win.geometry('800x600') #主窗口大小
        self.win.title("trade")
        matplotlib.use('TkAgg')
        self.layout(self.win)
        self.win.mainloop()

    def layout(self, parent):
        f = tk.Frame(parent)
        self.param_select_layout(f)
        f.pack(side=tk.TOP)
        f = tk.Frame(parent)
        self.tab_layout(f)
        f.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.YES)

    def param_select_layout(self, parent):
        self.plat = 'coinex'
        self.pair = 'btc_usdt'
        self.indicator_opt = ['bbands','macd', 'stoch']
        self.plat_opt = ['coinex','okex']
        self.pair_opt = ['btc_usdt','etc_usdt','eos_usdt','eth_usdt']
        self._opt = ['1','2']
        self.add_frame_combobox(parent, self.indicator_opt, self.indicator_select, side=tk.LEFT)
        self.add_frame_combobox(parent, self.plat_opt, self.plat_select, side=tk.LEFT)
        self.add_frame_combobox(parent, self.pair_opt, self.pair_select, side=tk.LEFT)
        self.add_frame_combobox(parent, self._opt, self._select, side=tk.LEFT)

    def add_frame_combobox(self, parent, options, func, **params):
        f = tk.Frame(parent, height=80, width=100)
        f.pack(**params)
        comb = ttk.Combobox(f,textvariable=tk.StringVar())
        comb['values'] = options
        comb.bind('<<ComboboxSelected>>', func)
        comb.pack()

    def indicator_select(self, event):
        indicator = event.widget.get()
        sslot.indicator_select(indicator)

    def plat_select(self, event):
        plat = event.widget.get()
        sslot.indicator_select(plat)

    def pair_select(self, event):
        pair = event.widget.get()
        sslot.indicator_select(pair)

    def _select(self, event):
        other = event.widget.get()
        sslot.indicator_select(other)

    def tab_layout(self, parent):
        tabs=OrderedDict([("分析",None), ("行情",None), ("交易",None), ("机器人",None), ("debug", None)])
        tab = ttk.Notebook(parent)
        for key in tabs.keys():#sorted(tabs.keys()):
            tabs[key] = ttk.Frame(tab)
            tab.add(tabs[key], text=key)
        tab.pack(expand=1, fill="both")

        self.markettab = MarketTab()
        self.markettab.layout(tabs['行情'])
        self.tradetab = TradeTab()
        self.tradetab.layout(tabs['交易'])
        self.analysistab = AnalysisTab()
        self.analysistab.layout(tabs['分析'])
        self.robottab = RobotTab()
        self.robottab.layout(tabs['机器人'])
        self.debugtab = DebugTab()
        self.debugtab.layout(tabs['debug'])

    def exit(self):
        self.markettab.exit()
        self.tradetab.exit()
        self.analysistab.exit()
        self.robottab.exit()
        self.debugtab.exit()
        self.win.quit()
        self.win.destroy()


class AnalysisTab():
    def __init__(self):
        #super(AnalysisTab, self).__init__()
        self.kl = pd.DataFrame()
        self.trade_history = []

    def layout(self, parent):
        fig,self.ta_axes = plt.subplots(2,1,sharex=True)
        self.ta_canva =FigureCanvasTkAgg(fig, master=parent)
        self.ta_canva.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        self.ta_canva._tkcanvas.pack(fill=tk.BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg(self.ta_canva, parent)
        toolbar.update()
        ###data graphic
        self.bbands = Bbands()
        self.macd = Macd()
        self.stoch = Stoch()
        self.indicator = cfg.get_indicator()
        mkt.register_handle('kline', self.bbands.handle_data)
        mkt.register_handle('kline', self.macd.handle_data)
        mkt.register_handle('kline', self.stoch.handle_data)
        #mkt.register_handle('depth', win.handle_depth)
        mkt.register_handle('kline', self.handle_kline)
        sslot.register_trade_log(self.handle_trade_log)
        ###options handle
        sslot.register_indicator_select(self.indicator_select)
        sslot.register_plat_select(self.plat_select)
        sslot.register_pair_select(self.pair_select)
        sslot.register_other_select(self._select)

    def draw(self):
        self.ta_axes[0].cla()
        self.ta_axes[1].cla()
        if self.indicator == 'bbands':
            ta_graphic('price', self.ta_axes[1], self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('bbands', self.ta_axes[1], self.bbands.get_data())
        elif self.indicator == 'macd':
            ta_graphic('price', self.ta_axes[0], self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('macd', self.ta_axes[1], self.macd.get_data())
        elif self.indicator == 'stoch':
            ta_graphic('price', self.ta_axes[0], self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('stoch', self.ta_axes[1], self.stoch.get_data())
        else:
            pass
        self.ta_canva.draw()
        
    def handle_depth(self, timestamp, depth):
#        print("win handle depth",price_history)
#        ta_graphic('price', self.ta_axes[0], pd.DataFrame(price_history, columns = ['t','price']))
#        self.ta_canva.draw()
        pass

    def handle_kline(self, kl):
        self.kl = kl
        self.draw()

    def handle_trade_log(self, log):
        if len(self.trade_history) > 100:
            self.trade_history.pop(0)
        self.trade_history.append(log)
        self.draw()

    def indicator_select(self, indicator):
        self.indicator = indicator
        if indicator == 'bbands':
            kl = self.bbands.get_kl()
        elif indicator == 'macd':
            kl = self.macd.get_kl()
        elif indicator == 'stoch':
            kl = self.stoch.get_kl()
        self.handle_kline(kl)

    def plat_select(self, plat):
        pass

    def pair_select(self, pair):
        pass

    def _select(self, other):
        pass

    def exit(self):
        mkt.unregister_handle('kline', self.bbands.handle_data)
        mkt.unregister_handle('kline', self.macd.handle_data)
        mkt.unregister_handle('kline', self.stoch.handle_data)
        mkt.unregister_handle('kline', self.handle_kline)
#        mkt.unregister_handle('depth', self.handle_depth)


class MarketTab():
    def __init__(self):
        #super(MarketTab, self).__init__()
        pass

    def layout(self, parent):
        pass

    def indicator_select(self, indicator):
        pass

    def plat_select(self, event):
        pass

    def pair_select(self, event):
        pass

    def _select(self, event):
        pass

    def exit(self):
        pass


class TradeTab():
    def __init__(self):
        #super(TradeTab, self).__init__()
        pass

    def layout(self, parent):
        pass

    def indicator_select(self, indicator):
        pass

    def plat_select(self, event):
        pass

    def pair_select(self, event):
        pass

    def _select(self, event):
        pass

    def exit(self):
        pass

class RobotTab():
    def __init__(self):
        #super(RobotTab, self).__init__()
        self.rbt = Robot()

    def layout(self, parent):
        f = tk.Frame(parent)
        self.scr = scrolledtext.ScrolledText(f)#, width=100, height=30)
        self.scr.pack(fill=tk.BOTH, expand=1)
        f.pack(side=tk.LEFT,fill=tk.BOTH, expand=1)
        
        f = tk.Frame(parent)
        ttk.Button(f,text='start',command=self.start).pack()
        ttk.Button(f,text='stop',command=self.stop).pack()
        ttk.Button(f,text='testback',command=self.testback).pack()
        f.pack(side=tk.LEFT)

        sslot.register_robot_log(self.handle_robot_log)

    def start(self):
        self.rbt.start()
        
    def stop(self):
        self.rbt.stop()

    def testback(self):
        self.rbt.testback()

    def handle_robot_log(self, msg):
        self.scr.insert(tk.END, msg+'\n')
        self.scr.see(tk.END)

    def indicator_select(self, indicator):
        pass

    def plat_select(self, event):
        pass

    def pair_select(self, event):
        pass

    def _select(self, event):
        pass

    def exit(self):
        self.rbt.stop()

class DebugTab():
    def __init__(self):
        #super(DebugTab, self).__init__()
        pass

    def layout(self, parent):
        btn = ttk.Button(parent,text='test',command=self.btn_click)
        btn.pack()
        self.plat_select_widget(parent)
        self.debug_label=tk.Label(parent,bg='pink', text='empty')
        self.debug_label.pack()

    def btn_click(self):
        pass
        
    def plat_select_widget(self, parent):
        self.plat=("okex","coinex","fcoin")
        self.platvar = tk.StringVar()
        self.platvar.set(0)

        lf=tk.LabelFrame(parent,  text="平台选择")
        for i in range(len(self.plat)):
            tk.Radiobutton(lf, variable=self.platvar, value=self.plat[i],
                        text=self.plat[i],indicatoron=0, width=10,
                        command=self.debug_label_update).pack()
        lf.pack()

    def debug_label_update(self):
        p = self.platvar.get()
        self.debug_label.config(text='platform selected:  '+p)

    def indicator_select(self, indicator):
        pass

    def plat_select(self, event):
        pass

    def pair_select(self, event):
        pass

    def _select(self, event):
        pass

    def exit(self):
        pass

if __name__ == '__main__':
    win = windows()
    win.mainloop()

