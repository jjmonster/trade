import tkinter as Tk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime,timedelta
import pandas as pd
from tanalyse import bbands,macd,stoch
from logger import log
import time

matplotlib.use('TkAgg')
root =Tk.Tk()
root.title("tanalyse")

def graphic(indicator, kl, data):
    print(kl, data)
    df = pd.DataFrame()
    if indicator == 'macd':
        df['zero'] = pd.Series([0]*kl['c'].size)
        df['price'] = pd.Series(kl['c'] - kl['c'].mean()) #price fixed around 0 for trend analyse
    elif indicator == 'stoch':
        #df['price'] = pd.Series(kl['c']*(50/kl['c'].mean())) #price fixed around 50 for trend analyse
        df['up'] = pd.Series([80]*kl['c'].size)
        df['low'] = pd.Series([20]*kl['c'].size)
        df['mid'] = pd.Series([50]*kl['c'].size)
        df['price'] = kl['c']
        df['dif'] = (data['slowk'] - data['slowd']) + 50
    elif indicator == 'stochrsi':
        df['up'] = pd.Series([80]*kl['c'].size)
        df['low'] = pd.Series([20]*kl['c'].size)
        df['mid'] = pd.Series([50]*kl['c'].size)
        df['price'] = kl['c']
    else:
        df['price'] = kl['c']
    df = pd.concat([df, data], axis=1)
    #print(df)
    _graphic(df, indicator, root)

def _graphic(df, title, parent):
    if title != 'bbands':
        fig, axes = plt.subplots(2,1,sharex=True, figsize=(12,8))
        ax1,ax2= axes[0],axes[1]
    else:
        fig = plt.figure(figsize=(12,8))
        ax1= fig.add_subplot(111)
    line_color = ('b','g','r','c','m','y','k')#,'w')
    line_maker = ('.',',','o') ###...
    line_style = ('-', '--', '-.', ':')

    t = list(map(datetime.fromtimestamp, df['t']))
    for i in range(df.columns.size): #exclude 't'
        if df.columns[i] == 't':
            continue
        column = df[df.columns[i]]
        lcs = line_color[int(i%len(line_color))]+line_style[int(i/len(line_color))]
        if title == 'bbands':
            ax1.plot(t, column, lcs)
        else:
            if df.columns[i] == 'price':
                ax1.plot(t, column, lcs)
            else:
                ax2.plot(t, column, lcs)

    ax1.set_title(title, fontproperties="SimHei")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
    ax1.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
    plt.xticks(rotation=45)
    plt.legend()
    #plt.show()
    #
    canvas =FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    #把matplotlib绘制图形的导航工具栏显示到tkinter窗口上
    toolbar =NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)


def on_key_event(event):
    print('you pressed %s'% event.key)
    key_press_handler(event, canvas, toolbar)
    canvas.mpl_connect('key_press_event', on_key_event)

def _quit():
    root.quit()
    root.destroy()


button =Tk.Button(master=root, text='Quit', command=_quit)
button.pack(side=Tk.BOTTOM)

graphic('bbands', bbands.get_kl(), bbands.get_data())
Tk.mainloop()
