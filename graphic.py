import tkinter as Tk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime,timedelta
import pandas as pd
from tanalyse import bbands,macd,stoch,ta_register,ta_unregister
from logger import log
import time

def _graphic(indicator, ax, df):
    line_color = ('b','g','r','c','m','y','k')#,'w')
    line_maker = ('.',',','o') ###...
    line_style = ('-', '--', '-.', ':')
    t = list(map(datetime.fromtimestamp, df['t']))
    for i in range(df.columns.size): #exclude 't'
        if df.columns[i] == 't':
            continue
        col = df[df.columns[i]]
        lcs = line_color[int(i%len(line_color))]+line_style[int(i/len(line_color))]
        ax.plot(t, col, lcs)

    ax.set_title(indicator, fontproperties="SimHei")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) #%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.DayLocator()) #HourLocator())
    plt.xticks(rotation=45)
    plt.legend()
    #plt.show()



def on_key_event(event):
    print('you pressed %s'% event.key)
    key_press_handler(event, canvas, toolbar)
    canvas.mpl_connect('key_press_event', on_key_event)

def _quit():
    root.quit()
    root.destroy()


def test():
    matplotlib.use('TkAgg')
    root =Tk.Tk()
    root.title("tanalyse")

    button =Tk.Button(master=root, text='Quit', command=_quit)
    button.pack(side=Tk.BOTTOM)

    ta_register()
    fig = graphic('bbands', bbands.get_kl(), bbands.get_data())
    
    canvas =FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    #把matplotlib绘制图形的导航工具栏显示到tkinter窗口上
    #toolbar =NavigationToolbar2TkAgg(canvas, root)
    #toolbar.update()
    #canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    root.mainloop()
    ta_unregister()

#test()
