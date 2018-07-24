#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
from tkinter import *
from tkinter import ttk
from collections import OrderedDict

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from k_line import kline

class app:
    def __init__(self):
        self.win = Tk()
        self.win.geometry('800x600') #主窗口大小
        self.win.title("trade")
        self.tabs=OrderedDict([("行情",None), ("交易",None), ("分析",None), ("机器人",None), ("debug", None)])
        self.plat=("okex","coinex","fcoin")
        self.platvar = StringVar()
        self.platvar.set(0)
        self.kl = kline()

    def mainloop(self):
        self.win.mainloop()
            
    def tab_layout(self):
        tab = ttk.Notebook(self.win)
        for key in sorted(self.tabs.keys()):
            self.tabs[key] = ttk.Frame(tab)
            tab.add(self.tabs[key], text=key)
        tab.pack(expand=1, fill="both")
        self.tab_analysis_layout(self.tabs['分析'])
        self.tab_debug_layout(self.tabs['debug'])
        self.tab_market_layout(self.tabs['行情'])
        

    def debug_label_update(self):
        p = self.platvar.get()
        self.debug_label.config(text='platform selected:  '+p)
        
    def tab_debug_layout(self, parent):
        self.debug_label=Label(parent,bg='pink', text='empty')
        self.debug_label.pack()

    def plat_select_widget(self, parent, variable):
        lf=LabelFrame(parent,  text="平台选择")
        for i in range(len(self.plat)):
            Radiobutton(lf, variable=variable, value=self.plat[i],
                        text=self.plat[i],indicatoron=0, width=10,
                        command=self.debug_label_update).pack()
        return lf
        
    def tab_analysis_layout(self, parent):
        wg = self.plat_select_widget(parent, self.platvar)
        wg.pack()
        

    def tab_market_layout(self, parent):
        return
        

if __name__ == '__main__':
    root=app()
    root.tab_layout()
    root.mainloop()

