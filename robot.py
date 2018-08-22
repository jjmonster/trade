from config import cfg
from logger import log,hist
from framework import fwk
from market import mkt
from tanalyse import Bbands, Macd, Stoch
from utils import *

import time

class Robot():
    def __init__(self):
        #variables for mine
#        self.orig_balance=fwk.get_balance_all()
        self.coin1_fee=0.0 
        self.coin2_fee=0.0
#        self.order_id = []
#        self.old_price = []
        self.deficit_allowed = cfg.get_fee() * cfg.get_trans_fee() 
        self.exchange = 0
        
        #variables for trade record
        self.balance = {cfg.get_coin1():1, cfg.get_coin2():0}
        self.price_history = list() #time,price
        self.trade_history = list() #time,type,price,amount
        self.trade_type = {'open_buy':1, 'open_sell':2, 'loss_buy':3, 'loss_sell':4, 'margin_buy':3,'margin_sell':4}
        self.amount_hold = {'buy':0, 'sell':0, 'max':self.balance[cfg.get_coin1()]/2 if cfg.is_future() else 1000}
        self.profit = {'buy':0, 'sell':0, 'price':0, 'amount':self.amount_hold}

        #variables for technical indicator
        self.indicator = 'stoch'
        self.bbands = Bbands()
        self.macd = Macd()
        self.stoch = Stoch()

        #variables for trade signal
        self.prev_sig = ''
        self.bSignal = ''

        #variables for log print
        self.depth_handle = 0

        #variables for automatic running
        self.running = 0

        #variables for test back
        self.testing = False

    def _trade(self,timestamp, type_key, price, amount):
        ttype = self.trade_type[type_key]
        if fwk.trade(cfg.get_pair(), ttype, price, amount) == True:
            if ttype == 1:
               self.profit['buy'] -= price*amount 
               self.amount_hold['buy'] += amount
            elif ttype == 2:
                self.profit['sell'] -= price*amount
                self.amount_hold['sell'] += amount
            elif ttype == 3:
                self.profit['buy'] += price*amount
                self.amount_hold['buy'] -= amount
            elif ttype == 4:
                self.profit['sell'] += price*amount
                self.amount_hold['sell'] -= amount

            ##record the trade history
            if len(self.trade_history) > 100:
                self.trade_history.pop(0)
            else:
                self.trade_history.append([timestamp, type_key, price, amount])
            #log.info("trade history: %s"%(self.trade_history))
            hist.info("%s"%([timestamp, type_key, price, amount]))

        
    def trade(self, timestamp, signal, bp, ba, sp, sa):
        price = amount = 0
        if signal == 'buy':
            if self.amount_hold['sell'] > 0:
                type_key = 'margin_sell'
                a = self.amount_hold['sell']
            else:
                type_key = 'open_buy'
                a = self.amount_hold['max'] - self.amount_hold['buy']
            amount = min(a, sa)
            price = sp
        elif signal == 'sell':
            if self.amount_hold['buy'] > 0:
                type_key = 'margin_buy'
                a = self.amount_hold['buy']
            else:
                type_key = 'open_sell'
                a = self.amount_hold['max'] - self.amount_hold['sell']
            amount = min(a, ba)
            price = bp
        else: ## standby
            return

        if price > 0 and amount > 0:
            log.info("going to trade! type:%s price:%f, amount:%f"%(type_key, price, amount))
            self._trade(timestamp, type_key, price, amount) 

    def handle_depth(self, timestamp, depth):
        bp = depth['buy'][0][0]  #price buy
        ba = depth['buy'][0][1]  #amount buy
        sp = depth['sell'][0][0] #price sell
        sa = depth['sell'][0][1] #amount sell
        self.depth_handle += 1
        if self.depth_handle%60 == 0:
            ##log runtime profit
            runtime_profit = {}
            runtime_profit['buy'] = round(self.profit['buy'] + self.amount_hold['buy']*bp, 2)
            runtime_profit['sell'] = round(-(self.profit['sell'] + self.amount_hold['sell']*sp), 2) ##sell ticket have inverted profit
            runtime_profit['price'] = round((bp+sp)/2,6)
            runtime_profit['ahold'] = self.amount_hold
            log.dbg("runtime_profit:%s"%(runtime_profit))

        gap = gaps(bp, sp)
        if gap > 0.2:
            log.dbg("gap=%f low volume, don't operate!"%(gap))
            return

        self.bbands.ta_signal(timestamp, (bp+sp)/2)
        self.macd.ta_signal(timestamp, (bp+sp)/2)
        self.stoch.ta_signal(timestamp, (bp+sp)/2)
        if self.indicator == 'bbands':
            signal = self.stoch.sig   ##indicator change or mix
        elif self.indicator == 'macd':
            signal = self.macd.sig
        elif self.indicator == 'stoch':
            signal = self.stoch.sig
        else:
            signal = 'None'
        #log.dbg("get signal! %s"%signal)
        self.trade(timestamp, signal, bp, ba, sp, sa)

    def start(self):
        if self.running == 0:
            log.dbg("robot starting...")
            self.running = 1            
            mkt.register_handle('depth', self.handle_depth)
            mkt.register_handle('kline', self.bbands.handle_data)
            mkt.register_handle('kline', self.macd.handle_data)
            mkt.register_handle('kline', self.stoch.handle_data)
        else:
            log.dbg("robot already running!")

    def stop(self):
        if self.running == 1:
            log.dbg("robot stopping...")
            mkt.unregister_handle('depth', self.handle_depth)
            mkt.unregister_handle('kline', self.bbands.handle_data)
            mkt.unregister_handle('kline', self.macd.handle_data)
            mkt.unregister_handle('kline', self.stoch.handle_data)
            self.running = 0


    def test_back(self):
        self.testing = True
        days = 10
        kl_1hour = fwk.get_kline(cfg.get_pair(), dtype="1hour", limit=min(days*24, 2000))
        if kl_1hour.size > 0:
            self.bbands.handle_data(kl_1hour)
            self.macd.handle_data(kl_1hour)
            self.stoch.handle_data(kl_1hour)
            
        kl_1min = fwk.get_kline(cfg.get_pair(), dtype="1min", limit=min(days*24*60, 2000))
        if(kl_1min.size <= 0):
            return
        p = kl_1min['c']
        t = kl_1min['t']
        for i in range(t.size):
            dummy_depth = {'buy':[[p[i]*0.999, 1000]],'sell':[[p[i]*1.001, 1000]]}
            self.handle_depth(t[i], dummy_depth)
        self.testing = False
                

rbt = Robot()
if __name__ == '__main__':
    rbt.start()
    time.sleep(10000000)
    rbt.stop()
