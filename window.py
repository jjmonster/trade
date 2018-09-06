#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *
#import tkinter as tk
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
from framework import fwk
from market import mkt
from signalslot import sslot
from tanalyse import Bbands,Macd,Stoch
from robot import Robot
from threading import Thread


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
            cms = line_color[int(i%len(line_color))]+line_maker[0]+line_style[int(i/len(line_color))]
            ax.plot(t, col, cms)

    ax.set_title(indicator, fontproperties="SimHei")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
    ax.legend()
    plt.xticks(rotation=45)
    #plt.show()

    if len(params) > 1:
        hist = params[1]
        if hist.index.size > 0:
            for i in hist.index:
                row = hist.loc[i]
                time = datetime.fromtimestamp(row['t'])
                type = row['type']
                price = row['price']
                if type == 'open_buy':
                    cms = 'r+'
                elif type == 'margin_buy' or type == 'loss_buy':
                    cms = 'rx'
                elif type == 'open_sell':
                    cms = 'y+'
                elif type == 'margin_sell' or type == 'loss_sell':
                    cms = 'yx'
                ax.plot([time], [price], cms)

class windows:
    def __init__(self):
        pass

    def mainloop(self):
        self.win = Tk()
        #bind exit method
        self.win.protocol("WM_DELETE_WINDOW", self.exit)
        self.win.bind('<Escape>', lambda e: self.exit())

        #self.win.geometry('800x600') #主窗口大小
        self.win.title("trade")
        matplotlib.use('TkAgg')
        self.layout(self.win)
        self.win.mainloop()

    def layout(self, parent):
        f = Frame(parent)
        self.param_select_layout(f)
        f.pack(side=TOP)
        f = Frame(parent)
        self.tab_layout(f)
        f.pack(side=TOP,fill=BOTH, expand=YES)

    def param_select_layout(self, parent):
        #self.plat = 'coinex'
        #self.pair = 'btc_usdt'
        indicator_opt = ['bbands','macd', 'stoch','bbands+macd', 'stoch+macd']
        idx = indicator_opt.index(cfg.get_indicator())
        self.add_frame_combobox(parent, indicator_opt, idx, self.indicator_select, side=LEFT)
        plat_opt = ['coinex','okex']
        idx = plat_opt.index(cfg.get_cfg_plat())
        self.add_frame_combobox(parent, plat_opt, idx, self.plat_select, side=LEFT)
        pair_opt = fwk.get_all_pair()
        idx = pair_opt.index(cfg.get_pair())
        self.add_frame_combobox(parent, pair_opt, idx, self.pair_select, side=LEFT)
        future_or_spot_opt = ['future','spot']
        idx = 0 if cfg.is_future() else 1
        self.add_frame_combobox(parent, future_or_spot_opt, 0, self.future_or_spot_select, side=LEFT)

    def add_frame_combobox(self, parent, options, index, func, **params):
        f = Frame(parent, height=80, width=100)
        f.pack(**params)
        comb = ttk.Combobox(f,textvariable=StringVar())
        comb['values'] = options
        comb.current(index)
        comb.bind('<<ComboboxSelected>>', func)
        comb.pack()

    def indicator_select(self, event):
        indicator = event.widget.get()
        sslot.indicator_select(indicator)

    def plat_select(self, event):
        plat = event.widget.get()
        sslot.plat_select(plat)

    def pair_select(self, event):
        pair = event.widget.get()
        sslot.pair_select(pair)

    def future_or_spot_select(self, event):
        future_or_spot = event.widget.get()
        sslot.future_or_spot_select(future_or_spot)

    def tab_layout(self, parent):
        tabs=OrderedDict([("分析",None), ("行情",None), ("交易",None), ("机器人",None), ("debug", None)])
        tab = ttk.Notebook(parent)
        for key in tabs.keys():#sorted(tabs.keys()):
            tabs[key] = ttk.Frame(tab)
            tab.add(tabs[key], text=key)
        tab.pack(expand=YES, fill="both")

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
        self.trade_history = pd.DataFrame()

    def layout(self, parent):
        self.fig = plt.figure()
        #self.fig,self.ta_axes = plt.subplots(3,1,sharex=True)
        self.ta_canva =FigureCanvasTkAgg(self.fig, master=parent)
        self.ta_canva.get_tk_widget().pack(fill=BOTH, expand=YES)
        self.ta_canva._tkcanvas.pack(fill=BOTH, expand=YES)
        toolbar = NavigationToolbar2TkAgg(self.ta_canva, parent)
        toolbar.update()
        ###data graphic
        self.bbands = Bbands()
        self.macd = Macd()
        self.stoch = Stoch()
        self.bbands.start()
        self.macd.start()
        self.stoch.start()
        #mkt.register_handle('depth', win.handle_depth)
        mkt.register_handle('kline', self.handle_kline)
        sslot.register_trade_history(self.handle_trade_history)
        ###options handle
        sslot.register_indicator_select(self.indicator_select)
        sslot.register_plat_select(self.plat_select)
        sslot.register_pair_select(self.pair_select)
        sslot.register_future_or_spot_select(self.future_or_spot_select)

    def draw(self):
        self.fig.clf()
        indicator = cfg.get_indicator()
        if indicator == 'bbands':
            ax = self.fig.add_subplot(111)
            ta_graphic('price', ax, self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('bbands', ax, self.bbands.get_data())
        elif indicator == 'macd':
            ta_graphic('price', self.fig.add_subplot(211), self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('macd', self.fig.add_subplot(212), self.macd.get_data())
        elif indicator == 'stoch':
            ta_graphic('price', self.fig.add_subplot(211), self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('stoch', self.fig.add_subplot(212), self.stoch.get_data())
        elif indicator == 'bbands+macd':
            ax = self.fig.add_subplot(211)
            ta_graphic('price', ax, self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('bbands', ax, self.bbands.get_data())
            ta_graphic('macd', self.fig.add_subplot(212), self.macd.get_data())
        elif indicator == 'stoch+macd':
            ta_graphic('price', self.fig.add_subplot(311), self.kl.loc[:,['t','c']], self.trade_history)
            ta_graphic('stoch', self.fig.add_subplot(312), self.stoch.get_data())
            ta_graphic('macd', self.fig.add_subplot(313), self.macd.get_data())
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

    def handle_trade_history(self, hist):
        self.trade_history = hist
        self.draw()

    def indicator_select(self, indicator):
        if indicator == 'bbands' or indicator == 'bbands+macd':
            kl = self.bbands.get_kl()
        elif indicator == 'macd':
            kl = self.macd.get_kl()
        elif indicator == 'stoch' or indicator == 'stoch+macd':
            kl = self.stoch.get_kl()
        self.handle_kline(kl)

    def plat_select(self, plat):
        pass

    def pair_select(self, pair):
        pass

    def future_or_spot_select(self, future_or_spot):
        pass

    def exit(self):
        self.bbands.stop()
        self.macd.stop()
        self.stoch.stop()
        mkt.unregister_handle('kline', self.handle_kline)
#        mkt.unregister_handle('depth', self.handle_depth)
        sslot.unregister_trade_history(self.handle_trade_history)
        ###options handle
        sslot.unregister_indicator_select(self.indicator_select)
        sslot.unregister_plat_select(self.plat_select)
        sslot.unregister_pair_select(self.pair_select)
        sslot.unregister_future_or_spot_select(self.future_or_spot_select)



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

    def future_or_spot_select(self, event):
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

    def future_or_spot_select(self, event):
        pass

    def exit(self):
        pass

class RobotTab():
    def __init__(self):
        #super(RobotTab, self).__init__()
        self.rbt = Robot()

    def layout(self, parent):
        ########
        lf = LabelFrame(parent, text='Logs')
        self.scr = scrolledtext.ScrolledText(lf)#, width=100, height=30)
        self.scr.pack(fill=BOTH, expand=YES)
        lf.pack(side=LEFT,fill=BOTH, expand=YES)

        ########
        lf = LabelFrame(parent, text='Status')
        if cfg.is_future():
            lf1 = LabelFrame(lf, text='user_info',labelanchor=W)
            self.infolist = {}
            c1_info = self.rbt.user_info[cfg.get_coin1()]
            for i in c1_info.keys():
                if i == 'contracts':
                    for j in c1_info[i][0].keys():
                        self.infolist[j] =  Label(lf1, text=j+': '+str(c1_info[i][0][j]), width=20)
                        self.infolist[j].pack()
                else:
                    self.infolist[i] = Label(lf1, text=i+': '+str(c1_info[i]), width=20)
                    self.infolist[i].pack()
            lf1.pack(side=TOP,fill=X, expand=YES)

            if cfg.is_future():
                lf2 = LabelFrame(lf, text='position',labelanchor=W)
                self.positionlist = {}
                for i in self.rbt.future_position.keys():
                    self.positionlist[i] = Label(lf2, text=i+': '+str(self.rbt.future_position[i]), width=20)
                    self.positionlist[i].pack()
                lf2.pack(side=TOP,fill=X, expand=YES)

        lf.pack(side=LEFT,fill=BOTH, expand=YES)

        #########
        lf = LabelFrame(parent, text='Paramters')
        
        
        lf.pack(side=LEFT,fill=BOTH, expand=YES)
        
        #########
        lf = LabelFrame(parent, text='Action')
        ttk.Button(lf,text='start',command=self.start).pack()
        ttk.Button(lf,text='stop',command=self.stop).pack()
        ttk.Button(lf,text='testback',command=self.testback).pack()
        lf.pack(side=LEFT,fill=BOTH, expand=YES)

        #####
        sslot.register_robot_status(self.handle_robot_status)
        sslot.register_robot_log(self.handle_robot_log)

    def start(self):
        self.rbt.start()
        
    def stop(self):
        self.rbt.stop()

    def testback(self):
        Thread(target = self.rbt.testback).start()

    def handle_robot_log(self, msg):
        self.scr.insert(END, msg+'\n')
        self.scr.see(END)

    def handle_robot_status(self, status):
        c1_info = self.rbt.user_info[cfg.get_coin1()]
        for i in c1_info.keys():
            if i == 'contracts':
                for j in c1_info[i][0].keys():
                    val = c1_info[i][0][j]
                    if isinstance(val, str):
                        text = j+': '+val
                    else:
                        text = j+': '+str(round(val, 6))
                    self.infolist[j].config(text=text)

            else:
                val = c1_info[i]
                if isinstance(val, str):
                    text = i+': '+val
                else:
                    text = i+': '+str(round(val, 6))
                self.infolist[i].config(text=text)

        if cfg.is_future():
            for i in self.rbt.future_position.keys():
                val = self.rbt.future_position[i]
                if isinstance(val, str):
                    text = i+': '+val
                else:
                    text = i+': '+str(round(val, 6))
                self.positionlist[i].config(text=text)

    def indicator_select(self, indicator):
        pass

    def plat_select(self, event):
        pass

    def pair_select(self, event):
        pass

    def future_or_spot_select(self, event):
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
        self.debug_label=Label(parent,bg='pink', text='empty')
        self.debug_label.pack()

    def btn_click(self):
        pass
        
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

    def indicator_select(self, indicator):
        pass

    def plat_select(self, event):
        pass

    def pair_select(self, event):
        pass

    def future_or_spot_select(self, event):
        pass

    def exit(self):
        pass

if __name__ == '__main__':
    win = windows()
    win.mainloop()

