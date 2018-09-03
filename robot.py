from collections import OrderedDict,defaultdict
from config import cfg
from logger import log,hist
from framework import fwk
from market import mkt
from tanalyse import Bbands, Macd, Stoch
from signalslot import sslot
from utils import *

import time

class Robot():
    def __init__(self):
        self.simulate = True
        self.orig_balance = defaultdict(lambda:defaultdict(lambda:0))
        self.curr_balance = defaultdict(lambda:defaultdict(lambda:0))

        #variables for mine
        self.coin1_fee=0.0
        self.coin2_fee=0.0
        self.order_id = []
        self.deficit_allowed = cfg.get_fee() * cfg.get_trans_fee() 
        self.exchange = 0
        
        #variables for trade record
        self.update_variables()
        self.trade_type = {'open_buy':1, 'open_sell':2, 'loss_buy':3, 'loss_sell':4, 'margin_buy':3,'margin_sell':4}


        #variables for technical indicator
        self.bbands = Bbands()
        self.macd = Macd()
        self.stoch = Stoch()

        #variables for log print
        self.n_depth_handle = 0

        #variables for automatic running
        self.running = 0

        #variables for test back
        self.testing = False

    def update_variables(self, trade_param):
        if trade_param == None:
            self.n_depth_handle = 0
            self.price_history = []
            self.trade_history = []
        plat = cfg.get_cfg_plat()
        if plat == 'okex':
            if self.simulate:
                if trade_param == None:
                    ##init
                    self.user_info = {}
                    if cfg.is_future():
                        self.future_position = {}
                else:
                    ##update
                    self.user_info = {}
                    if cfg.is_future():
                        self.future_position = {}
            else:
                ##init or update directly
                self.user_info = fwk.get_user_info()
                if cfg.is_future():
                    self.future_position = fwk.get_future_position(cfg.get_pair())
        
        elif plat == 'coinex':
            c1 = cfg.get_coin1()
            c2 = cfg.get_coin2()
            if self.simulate:
                if trade_param == None:
                    ##init
                    self.curr_fund = self.orig_fund = 1000
                    self.orig_balance[c2]['available'] = self.orig_fund
                    self.curr_balance = self.orig_balance
                else:
                    ##update
                    self.curr_fund = self.orig_fund = 1000
                    self.orig_balance[c2]['available'] = self.orig_fund
                    self.curr_balance = self.orig_balance
            else:
                ##init or update directly
                self.curr_balance = self.orig_balance = {c1:fwk.get_balance(c1), c2:fwk.get_balance(c2)}
                price = fwk.get_price(cfg.get_pair())
                self.curr_fund = self.orig_fund = self.orig_balance[c1]['balance']*price + self.orig_balance[c2]['balance']

    def _trade(self,timestamp, type_key, price, amount, match_price=0):
        ttype = self.trade_type[type_key]
        if fwk.trade(cfg.get_pair(), ttype, price, amount, match_price) == True:
            ##record the trade history
            trade_param = [timestamp, type_key, price, amount, match_price]
            if len(self.trade_history) > 100:
                self.trade_history.pop(0)
            else:
                self.trade_history.append(trade_param)
            #log.info("trade history: %s"%(self.trade_history))
            hist.info("%s"%trade_param)
            sslot.trade_log(trade_param)
            self.update_variables(trade_param)
        
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
                if cfg.is_future():
                    type_key = 'open_sell'
                    a = self.amount_hold['max'] - self.amount_hold['sell']
                else: ########spot have no sell ticket
                    return
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
        self.n_depth_handle += 1
        if self.n_depth_handle%60 == 0:
            ##log runtime profit
            self.runtime_profit['buy'] = round(self.profit['buy'] + self.amount_hold['buy']*bp, 2)
            self.runtime_profit['sell'] = round(-(self.profit['sell'] + self.amount_hold['sell']*sp), 2) ##sell ticket have inverted profit
            self.runtime_profit['price'] = round((bp+sp)/2,6)
            log.dbg("runtime_profit:%s amount:%s"%(self.runtime_profit, self.amount_hold))
            ########
            sslot.robot_log("runtime_profit:%s amount:%s"%(self.runtime_profit, self.amount_hold))

        gap = gaps(bp, sp)
        if gap > 0.2:
            log.dbg("gap=%f low volume, don't operate!"%(gap))
            sslot.robot_log("gap=%f low volume, don't operate!"%(gap))
            return

        indicator = cfg.get_indicator()
        if indicator == 'bbands':
            self.bbands.ta_signal(timestamp, (bp+sp)/2)
            signal = self.stoch.sig
        elif indicator == 'macd':
            self.macd.ta_signal(timestamp, (bp+sp)/2)
            signal = self.macd.sig
        elif indicator == 'stoch':
            self.stoch.ta_signal(timestamp, (bp+sp)/2)
            signal = self.stoch.sig
        else:
            signal = 'None'
        #log.dbg("get signal! %s"%signal)
        self.trade(timestamp, signal, bp, ba, sp, sa, 0)

    def start(self):
        if self.running == 0:
            log.dbg("robot starting...")
            self.running = 1
            self.init_variables()
            self.bbands.start()
            self.macd.start()
            self.stoch.start()
            mkt.register_handle('depth', self.handle_depth)
        else:
            log.dbg("robot already running!")

    def stop(self):
        if self.running == 1:
            log.dbg("robot stopping...")
            mkt.unregister_handle('depth', self.handle_depth)
            self.bbands.stop()
            self.macd.stop()
            self.stoch.stop()
            self.running = 0


    def testback(self):
        self.testing = True
        days = 10
        kl_1hour = fwk.get_kline(cfg.get_pair(), dtype="1hour", limit=min(days*24, 2000))
        if kl_1hour.size > 0:
            self.bbands.handle_data(kl_1hour)
            self.macd.handle_data(kl_1hour)
            self.stoch.handle_data(kl_1hour)
            
        #kl_1min = fwk.get_kline(cfg.get_pair(), dtype="1min", limit=min(days*24*60, 2000))
        #if(kl_1min.size <= 0):
        #    return
        #p = kl_1min['c']
        #t = kl_1min['t']
        p = kl_1hour['c']
        t = kl_1hour['t']
        for i in range(t.size):
            dummy_depth = {'buy':[[p[i]*0.999, 1000]],'sell':[[p[i]*1.001, 1000]]}
            self.handle_depth(t[i], dummy_depth)
        self.testing = False
                

if __name__ == '__main__':
    rbt = Robot()
    rbt.start()
    time.sleep(10000000)
    rbt.stop()
