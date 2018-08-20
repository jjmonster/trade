#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *
from tkinter import ttk
from collections import OrderedDict

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
#from matplotlib.figure import Figure

from mpl_finance import candlestick_ochl,candlestick2_ochl
from datetime import datetime,timedelta

from market import mkt
from tanalyse import bbands, stoch, ta_register, ta_unregister
from robot import rbt

import numpy as np
import pandas as pd


def ta_graphic(indicator, ax, df):
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
    plt.xticks(rotation=45)
    plt.legend()
    #plt.show()

def trade_graphic(ax, hist):
    if len(hist) > 0:
        for i in range(len(hist)):
            time = datetime.fromtimestamp(hist[i][0])
            type = hist[i][1]
            price = hist[i][2]
            if type == 'open_buy' or type == 'margin_sell' or type == 'loss_sell':
                cms = 'ro'
            elif type == 'open_sell' or type == 'margin_buy' or type == 'loss_buy':
                cms = 'go'
            ax.plot([time], [price], cms)
        

class windows:
    def __init__(self):
        self.win = Tk()
        #bind exit method
        self.win.protocol("WM_DELETE_WINDOW", self.exit)
        self.win.bind('<Escape>', lambda e: self.exit())

        self.win.geometry('800x600') #主窗口大小
        self.win.title("trade")
        matplotlib.use('TkAgg')


    def mainloop(self):
        ta_register()
        self.layout()
        mkt.register_handle('kline', win.handle_kline)
        #mkt.register_handle('depth', win.handle_depth)
        self.win.mainloop()

    def layout(self):
        self.param_select_layout(self.win)
        self.tab_layout(self.win)

    def param_select_layout(self, parent):
        pass

    def tab_layout(self, parent):
        tabs=OrderedDict([("分析",None), ("行情",None), ("交易",None), ("机器人",None), ("debug", None)])
        tab = ttk.Notebook(parent)
        
        for key in tabs.keys():#sorted(tabs.keys()):
            tabs[key] = ttk.Frame(tab)
            tab.add(tabs[key], text=key)
        tab.pack(expand=1, fill="both")

        self.tab_market_layout(tabs['行情'])
        self.tab_trade_layout(tabs['交易'])
        self.tab_analysis_layout(tabs['分析'])
        self.tab_robot_layout(tabs['机器人'])
        self.tab_debug_layout(tabs['debug'])


    def tab_market_layout(self, parent):
        return

    def tab_trade_layout(self, parent):
        return

    def tab_analysis_layout(self, parent):
        fig,self.ta_axes = plt.subplots(2,1,sharex=True) #, figsize=(12,8))
        self.ta_canva =FigureCanvasTkAgg(fig, master=parent)
        self.ta_canva.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.ta_canva._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg(self.ta_canva, parent)
        toolbar.update()
        #btn = ttk.Button(parent,text='test',command=self.btn_click)
        #btn.pack()


    def tab_robot_layout(self, parent):
        return
        
    def tab_debug_layout(self, parent):
        self.plat_select_widget(parent)
        self.debug_label=Label(parent,bg='pink', text='empty')
        self.debug_label.pack()


    def handle_depth(self, timestamp, depth):
#        print("win handle depth",price_history)
#        ta_graphic('price', self.ta_axes[0], pd.DataFrame(price_history, columns = ['t','price']))
#        self.ta_canva.draw()
        pass

    def handle_kline(self, kl):
        ta_graphic('price', self.ta_axes[1], kl.loc[:,['t','c']])
        ta_graphic('bbands', self.ta_axes[1], bbands.get_data())
        trade_graphic(self.ta_axes[1], rbt.trade_history)
        self.ta_canva.draw()

    def btn_click(self):
        #self.ta_axes[0].cla()
        self.ta_canva.draw()
        
    def plat_select_widget(self, parent):
        self.plat=("okex","coinex","fcoin")
        self.platvar = StringVar()
        self.platvar.set(0)

        lf=LabelFrame(parent,  text="平台选择")
        for i in range(len(self.plat)):
            Radiobutton(lf, variable=self.platvar, value=self.plat[i],
                        text=self.plat[i],indicatoron=0, width=10,
                        command=self.debug_label_update).pack()
        lf.pack()

    def debug_label_update(self):
        p = self.platvar.get()
        self.debug_label.config(text='platform selected:  '+p)


    def exit(self):
        ta_unregister()
        mkt.unregister_handle('kline', self.handle_kline)
#        mkt.unregister_handle('depth', self.handle_depth)
        self.win.quit()
        self.win.destroy()

win = windows()
if __name__ == '__main__':
    ta_register()
    mkt.register_handle('kline', win.handle_kline)
#    mkt.register_handle('depth', win.handle_depth)
    win.layout()
    win.mainloop()

